from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

PARSED = {
    "name": "Ada Lovelace",
    "summary": "ML engineer",
    "education": "Cambridge",
    "skills": ["python", "pytorch"],
    "experience": ["ML Engineer @ Analytical Engines"],
    "projects": ["Built a RAG system"],
    "field": "nlp",
    "resume_text": "Full resume text...",
}


def test_upload_resume_rejects_non_pdf(fake_supabase):
    client = TestClient(app)
    response = client.post(
        "/resume/upload", files={"file": ("resume.txt", b"not a pdf", "text/plain")}
    )
    assert response.status_code == 400


def test_upload_resume_parses_and_stores_candidate(fake_supabase):
    client = TestClient(app)

    with patch("app.routes.resume.parse_resume_pdf", return_value=PARSED) as mock_parse:
        response = client.post(
            "/resume/upload",
            files={"file": ("resume.pdf", b"%PDF-1.4 fake bytes", "application/pdf")},
        )

    assert response.status_code == 200
    mock_parse.assert_called_once()

    body = response.json()
    assert body["field"] == "nlp"
    assert body["resume_sections"]["name"] == "Ada Lovelace"

    stored = fake_supabase.rows["candidates"]
    assert len(stored) == 1
    assert stored[0]["name"] == "Ada Lovelace"
    assert stored[0]["field"] == "nlp"
    assert stored[0]["resume_text"] == "Full resume text..."
