from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_unhandled_exception_returns_json_with_cors_headers(fake_supabase):
    """Regression test: an unhandled exception used to skip CORSMiddleware
    entirely, so the browser reported a misleading "CORS policy" error instead
    of the real one. Found by actually driving the app in a browser."""
    # raise_server_exceptions=False: we're testing the actual HTTP response a real
    # client gets, not Python-level exception propagation inside the test process.
    client = TestClient(app, raise_server_exceptions=False)

    with patch("app.routes.resume.parse_resume_pdf", side_effect=RuntimeError("boom")):
        response = client.post(
            "/resume/upload",
            files={"file": ("resume.pdf", b"%PDF-1.4 fake bytes", "application/pdf")},
            headers={"Origin": "http://localhost:5173"},
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "RuntimeError: boom"}
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
