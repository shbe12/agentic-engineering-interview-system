import base64
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.resume.parser import parse_resume_pdf

PARSED = {
    "name": "Ada Lovelace",
    "summary": "ML engineer",
    "education": "Cambridge",
    "skills": ["python"],
    "experience": ["ML Engineer @ Analytical Engines"],
    "projects": ["Built a RAG system"],
    "field": "nlp",
    "resume_text": "Full resume text...",
}


def test_parse_resume_pdf_sends_document_block_and_parses_result(tmp_path):
    pdf_bytes = b"%PDF-1.4 fake bytes"
    pdf_path = tmp_path / "resume.pdf"
    pdf_path.write_bytes(pdf_bytes)

    fake_response = SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(PARSED))])
    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_response

    with patch("app.resume.parser.get_anthropic_client", return_value=fake_client):
        result = parse_resume_pdf(str(pdf_path))

    assert result == PARSED

    _, kwargs = fake_client.messages.create.call_args
    content_blocks = kwargs["messages"][0]["content"]
    doc_block = next(b for b in content_blocks if b["type"] == "document")
    assert doc_block["source"]["type"] == "base64"
    assert doc_block["source"]["media_type"] == "application/pdf"
    assert base64.standard_b64decode(doc_block["source"]["data"]) == pdf_bytes
    assert kwargs["output_config"]["format"]["type"] == "json_schema"
