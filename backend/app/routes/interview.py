import io
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.evaluation.report import get_report
from app.interview.orchestrator import handle_message, start_session
from app.models.schemas import (
    MessageRequest,
    MessageResponse,
    ReportResponse,
    SpeakRequest,
    StartInterviewRequest,
    StartInterviewResponse,
    VoiceMessageResponse,
)
from app.voice.anxiety import detect_anxiety
from app.voice.stt import transcribe
from app.voice.tts import synthesize

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/start", response_model=StartInterviewResponse)
async def start(req: StartInterviewRequest) -> StartInterviewResponse:
    result = start_session(req.candidate_id)
    return StartInterviewResponse(**result)


@router.post("/message", response_model=MessageResponse)
async def message(req: MessageRequest) -> MessageResponse:
    result = handle_message(req.session_id, req.content)
    return MessageResponse(**result)


@router.post("/voice", response_model=VoiceMessageResponse)
async def voice_message(session_id: str, file: UploadFile) -> VoiceMessageResponse:
    with tempfile.NamedTemporaryFile(suffix=Path(file.filename or "audio.webm").suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        transcript = transcribe(str(tmp_path))
    finally:
        tmp_path.unlink(missing_ok=True)

    anxiety = detect_anxiety(
        transcript["text"], transcript["duration_seconds"], transcript["word_count"]
    )

    content = transcript["text"]
    reassurance_note = None
    if anxiety["anxious"]:
        content = f"[VOICE: candidate sounds anxious — {anxiety['reason']}] {content}"
        reassurance_note = f"Anxiety heuristic triggered: {anxiety['reason']}"

    result = handle_message(session_id, content)

    return VoiceMessageResponse(
        **result,
        anxiety_detected=anxiety["anxious"],
        reassurance_note=reassurance_note,
    )


@router.post("/speak")
async def speak(req: SpeakRequest) -> StreamingResponse:
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text must not be empty")
    audio_bytes = synthesize(req.text)
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")


@router.get("/{session_id}/report", response_model=ReportResponse)
async def report(session_id: str) -> ReportResponse:
    data = get_report(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not available yet — interview not completed.")
    return ReportResponse(**data)
