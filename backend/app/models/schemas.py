from typing import Any, Literal

from pydantic import BaseModel

Field = Literal["nlp", "cv", "other"]
Role = Literal["interviewer", "candidate"]


class ResumeUploadResponse(BaseModel):
    candidate_id: str
    resume_sections: dict[str, Any]
    field: Field


class StartInterviewRequest(BaseModel):
    candidate_id: str


class StartInterviewResponse(BaseModel):
    session_id: str
    phase: int
    message: str


class MessageRequest(BaseModel):
    session_id: str
    content: str


class MessageResponse(BaseModel):
    phase: int
    reply: str
    status: Literal["in_progress", "completed"]


class VoiceMessageResponse(MessageResponse):
    anxiety_detected: bool
    reassurance_note: str | None = None


class PhaseScore(BaseModel):
    phase: int
    score: float | None
    notes: str


class ReportResponse(BaseModel):
    session_id: str
    summary: str
    per_phase_scores: dict[str, float | None]


class SpeakRequest(BaseModel):
    text: str
