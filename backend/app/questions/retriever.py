"""Field-based similarity retrieval over the MLQuestions bank (data/ml_questions.md),
using a local 384-dim embedding model, with a GPT-generated fallback when nothing
relevant is found — per spec: "If you can't find questions in this document, create
these questions yourself. And the question should have a factually correct answer."
"""

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from app.llm import chat_json

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "ml_questions.md"


# Root README uses "#### N) Question [[src]]"; the NLP README uses "### N. Question [[src]]".
_QUESTION_RE = re.compile(r"^#{3,4}\s*\d+[.)]\s*(.+?)\s*(?:\[\[.*?\]\].*)?$")
_FIELD_MARKER_RE = re.compile(r"<!--\s*field:\s*(\w+)\s*-->")


@dataclass
class QAEntry:
    field: str
    question: str
    answer: str


def _parse_markdown(text: str) -> list[QAEntry]:
    entries: list[QAEntry] = []
    current_field = "other"
    current_question: str | None = None
    current_answer_lines: list[str] = []

    def flush() -> None:
        if current_question is not None:
            answer = "\n".join(current_answer_lines).strip()
            entries.append(QAEntry(field=current_field, question=current_question, answer=answer))

    for line in text.splitlines():
        field_match = _FIELD_MARKER_RE.match(line.strip())
        if field_match:
            flush()
            current_question = None
            current_answer_lines = []
            current_field = field_match.group(1)
            continue

        q_match = _QUESTION_RE.match(line.strip())
        if q_match:
            flush()
            current_question = q_match.group(1)
            current_answer_lines = []
            continue

        if current_question is not None:
            current_answer_lines.append(line)

    flush()
    return [e for e in entries if e.question and e.answer]


@lru_cache
def _load_entries() -> list[QAEntry]:
    if not DATA_PATH.exists():
        return []
    return _parse_markdown(DATA_PATH.read_text(encoding="utf-8"))


class _OnnxMiniLM:
    """Runs sentence-transformers/all-MiniLM-L6-v2 via ONNX Runtime (quantized
    weights), reproducing SentenceTransformer's mean-pooling + L2-normalization
    recipe, without a PyTorch dependency. PyTorch alone is ~750MB even in its
    CPU-only build — over Vercel's 500MB function size limit by itself. The
    quantized ONNX weights (~23MB) plus onnxruntime + transformers'
    tokenizer-only base (no torch extra) fit comfortably. Exposes the same
    `.encode(inputs, normalize_embeddings=True)` interface SentenceTransformer
    did, so callers below are unchanged.
    """

    MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
    ONNX_FILE = "onnx/model_quint8_avx2.onnx"

    def __init__(self):
        from huggingface_hub import hf_hub_download
        from transformers import AutoTokenizer
        import onnxruntime as ort

        # /tmp is the one writable path on Vercel's serverless filesystem;
        # explicit rather than relying on HF's default (~/.cache), which may
        # not be writable there.
        cache_dir = os.environ.get("HF_HOME", "/tmp/hf_cache")
        self._tokenizer = AutoTokenizer.from_pretrained(self.MODEL_ID, cache_dir=cache_dir)
        onnx_path = hf_hub_download(repo_id=self.MODEL_ID, filename=self.ONNX_FILE, cache_dir=cache_dir)
        self._session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        self._input_names = {i.name for i in self._session.get_inputs()}

    def encode(self, inputs, normalize_embeddings: bool = True) -> np.ndarray:
        single = isinstance(inputs, str)
        texts = [inputs] if single else list(inputs)
        encoded = self._tokenizer(texts, padding=True, truncation=True, return_tensors="np")
        onnx_inputs = {k: v for k, v in encoded.items() if k in self._input_names}
        token_embeddings = self._session.run(None, onnx_inputs)[0]

        attention_mask = np.expand_dims(encoded["attention_mask"], -1).astype(np.float32)
        summed = (token_embeddings * attention_mask).sum(axis=1)
        counts = np.clip(attention_mask.sum(axis=1), a_min=1e-9, a_max=None)
        pooled = summed / counts

        if normalize_embeddings:
            norms = np.linalg.norm(pooled, axis=1, keepdims=True)
            pooled = pooled / norms

        return pooled[0] if single else pooled


@lru_cache
def _embedder():
    return _OnnxMiniLM()  # 384-dim


@lru_cache
def _entry_embeddings() -> np.ndarray:
    entries = _load_entries()
    if not entries:
        return np.zeros((0, 384))
    model = _embedder()
    return model.encode([e.question for e in entries], normalize_embeddings=True)


def _cosine_top_k(query_embedding: np.ndarray, matrix: np.ndarray, k: int) -> list[int]:
    if matrix.shape[0] == 0:
        return []
    scores = matrix @ query_embedding
    k = min(k, len(scores))
    return list(np.argsort(-scores)[:k])


FALLBACK_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                },
                "required": ["question", "answer"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["questions"],
    "additionalProperties": False,
}


def _generate_fallback_questions(field: str, k: int) -> list[QAEntry]:
    result = chat_json(
        system_prompt=(
            "You write factual machine learning interview questions with factually "
            "correct, concise answers. Never fabricate incorrect answers."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generate {k} factual ML engineering interview questions "
                    f"(field: {field}), each with a correct, concise answer."
                ),
            }
        ],
        schema=FALLBACK_SCHEMA,
        schema_name="fallback_questions",
    )
    return [
        QAEntry(field=field, question=q["question"], answer=q["answer"])
        for q in result["questions"]
    ]


def retrieve_questions(resume_text: str, field: str, k: int = 5) -> list[QAEntry]:
    entries = _load_entries()
    pool_field = field if field == "nlp" else "cv"  # "other"/"cv" both draw from the general pool
    pool_indices = [i for i, e in enumerate(entries) if e.field == pool_field]

    if not pool_indices:
        return _generate_fallback_questions(field, k)

    model = _embedder()
    query_embedding = model.encode(resume_text, normalize_embeddings=True)
    pool_matrix = _entry_embeddings()[pool_indices]
    top = _cosine_top_k(query_embedding, pool_matrix, k)

    if not top:
        return _generate_fallback_questions(field, k)

    return [entries[pool_indices[i]] for i in top]
