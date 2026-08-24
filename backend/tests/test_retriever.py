from unittest.mock import patch

import numpy as np
import pytest

from app.questions import retriever


class FakeEmbedder:
    """Deterministic stand-in for SentenceTransformer — avoids downloading/loading
    the real MiniLM model in unit tests, matching how we mock other external/heavy
    boundaries (LLM, DB) elsewhere in the suite."""

    def encode(self, inputs, normalize_embeddings=True):
        single = isinstance(inputs, str)
        texts = [inputs] if single else list(inputs)
        vectors = []
        for text in texts:
            vec = np.zeros(384)
            vec[abs(hash(text)) % 384] = 1.0
            vectors.append(vec)
        arr = np.array(vectors)
        return arr[0] if single else arr


@pytest.fixture(autouse=True)
def _clear_retriever_caches():
    retriever._load_entries.cache_clear()
    retriever._entry_embeddings.cache_clear()
    retriever._embedder.cache_clear()
    yield
    retriever._load_entries.cache_clear()
    retriever._entry_embeddings.cache_clear()
    retriever._embedder.cache_clear()


@pytest.fixture(autouse=True)
def _fake_embedder():
    with patch("app.questions.retriever._embedder", return_value=FakeEmbedder()):
        yield


def test_parse_markdown_has_entries_for_both_fields():
    entries = retriever._load_entries()

    assert entries, "expected data/ml_questions.md to exist and parse into entries"
    fields = {e.field for e in entries}
    assert "nlp" in fields
    assert "cv" in fields
    for entry in entries[:5]:
        assert entry.question.strip()
        assert entry.answer.strip()


def test_retrieve_questions_returns_k_results_for_known_field():
    results = retriever.retrieve_questions("worked on transformer-based NLP models", "nlp", k=5)

    assert len(results) == 5
    assert all(r.field == "nlp" for r in results)


def test_retrieve_questions_falls_back_to_generated_when_pool_empty(monkeypatch):
    monkeypatch.setattr(retriever, "DATA_PATH", retriever.DATA_PATH.parent / "does-not-exist.md")
    retriever._load_entries.cache_clear()

    fallback = [{"question": "What is bias-variance tradeoff?", "answer": "..."}]
    with patch("app.questions.retriever.chat_json", return_value={"questions": fallback}) as mock_llm:
        results = retriever.retrieve_questions("some resume text", "nlp", k=1)

    mock_llm.assert_called_once()
    assert len(results) == 1
    assert results[0].question == "What is bias-variance tradeoff?"


def test_real_onnx_embedder_ranks_semantically_similar_questions_higher():
    """Exercises the real ONNX-backed MiniLM embedder end-to-end (not the
    FakeEmbedder the tests above use) to confirm actual semantic retrieval
    quality survived the PyTorch -> ONNX Runtime switch (see _OnnxMiniLM),
    not just the mocked plumbing. Downloads the quantized model + tokenizer
    from HF Hub on first run (cached under /tmp/hf_cache after)."""
    embedder = retriever._OnnxMiniLM()

    query = "What is the difference between stemming and lemmatization?"
    nlp_neighbor = "Explain how TF-IDF measures word importance."
    unrelated = "How does image registration work in computer vision?"

    vecs = embedder.encode([query, nlp_neighbor, unrelated], normalize_embeddings=True)
    sim_related = float(vecs[0] @ vecs[1])
    sim_unrelated = float(vecs[0] @ vecs[2])

    assert sim_related > sim_unrelated, (
        f"expected the semantically related NLP question ({sim_related:.4f}) to score "
        f"higher than the unrelated CV question ({sim_unrelated:.4f})"
    )
