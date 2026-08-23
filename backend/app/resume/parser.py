"""Resume PDF parsing — deliberately uses OpenAI's native file input instead of a
Python PDF library (pymupdf etc.), per the spec: "Maybe don't use a Python library
like pymupdf, etc. That's not very reliable."
"""

import json

from app.config import get_settings
from app.llm import get_openai_client

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
    client = get_openai_client()

    with open(file_path, "rb") as f:
        uploaded = client.files.create(file=f, purpose="user_data")

    response = client.responses.create(
        model=settings.openai_chat_model,
        reasoning={"effort": settings.openai_reasoning_effort},
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_file", "file_id": uploaded.id},
                    {"type": "input_text", "text": PARSE_INSTRUCTIONS},
                ],
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "resume_extraction",
                "schema": RESUME_SCHEMA,
                "strict": True,
            }
        },
    )
    return json.loads(response.output_text)
