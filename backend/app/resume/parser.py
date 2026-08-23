"""Resume PDF parsing — deliberately uses Claude's native document input instead of a
Python PDF library (pymupdf etc.), per the spec: "Maybe don't use a Python library
like pymupdf, etc. That's not very reliable."
"""

import base64
import json

from app.config import get_settings
from app.llm import MAX_TOKENS, get_anthropic_client

RESUME_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "summary": {"type": "string"},
        "education": {"type": "string"},
        "skills": {"type": "array", "items": {"type": "string"}},
        "experience": {"type": "array", "items": {"type": "string"}},
        "projects": {"type": "array", "items": {"type": "string"}},
        "field": {"type": "string", "enum": ["nlp", "cv", "other"]},
        "resume_text": {"type": "string"},
    },
    "required": [
        "name",
        "summary",
        "education",
        "skills",
        "experience",
        "projects",
        "field",
        "resume_text",
    ],
    "additionalProperties": False,
}

PARSE_INSTRUCTIONS = """You are parsing a candidate's resume PDF for a machine learning \
engineer mock-interview system. Extract:
- name
- summary (1-2 sentences)
- education (free text)
- skills (list)
- experience (list of strings, one per role/entry, most recent first)
- projects (list of strings, one per project, include enough detail that an interviewer \
could ask deep technical follow-up questions about it)
- field: classify the candidate's primary field as one of "nlp", "cv" (computer vision), \
or "other", based on their projects/experience
- resume_text: the full plain-text transcription of the resume

Return ONLY the structured fields — do not invent experience that isn't in the document."""


def parse_resume_pdf(file_path: str) -> dict:
    settings = get_settings()
    client = get_anthropic_client()

    with open(file_path, "rb") as f:
        pdf_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=MAX_TOKENS,
        output_config={
            "effort": settings.anthropic_effort,
            "format": {"type": "json_schema", "schema": RESUME_SCHEMA},
        },
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_b64,
                        },
                    },
                    {"type": "text", "text": PARSE_INSTRUCTIONS},
                ],
            }
        ],
    )
    text = next(block.text for block in response.content if block.type == "text")
    return json.loads(text)
