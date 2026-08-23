import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.db.client import get_supabase
from app.models.schemas import ResumeUploadResponse
from app.resume.parser import parse_resume_pdf

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile) -> ResumeUploadResponse:
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        # parse_resume_pdf is a blocking SDK call; run off the event loop so other
        # requests (including /health) aren't stalled for the duration of the call.
        parsed = await run_in_threadpool(parse_resume_pdf, str(tmp_path))
    finally:
        tmp_path.unlink(missing_ok=True)

    sections = {
        "name": parsed["name"],
        "summary": parsed["summary"],
        "education": parsed["education"],
        "skills": parsed["skills"],
        "experience": parsed["experience"],
        "projects": parsed["projects"],
    }

    supabase = get_supabase()
    result = (
        supabase.table("candidates")
        .insert(
            {
                "name": parsed["name"],
                "resume_text": parsed["resume_text"],
                "resume_sections": sections,
                "field": parsed["field"],
            }
        )
        .execute()
    )
    candidate_id = result.data[0]["id"]

    return ResumeUploadResponse(
        candidate_id=candidate_id,
        resume_sections=sections,
        field=parsed["field"],
    )
