from app.db.client import get_supabase
from app.interview.prompts import TURN_SCHEMA, build_system_prompt
from app.llm import chat_json, chat_text
from app.questions.retriever import retrieve_questions

TOTAL_PHASES = 5


def _load_candidate(candidate_id: str) -> dict:
    supabase = get_supabase()
    result = supabase.table("candidates").select("*").eq("id", candidate_id).single().execute()
    return result.data


def _load_session(session_id: str) -> dict:
    supabase = get_supabase()
    result = supabase.table("interview_sessions").select("*").eq("id", session_id).single().execute()
    return result.data


def _load_history(session_id: str) -> list[dict]:
    supabase = get_supabase()
    result = (
        supabase.table("interview_messages")
        .select("role, content")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    role_map = {"interviewer": "assistant", "candidate": "user"}
    return [{"role": role_map[m["role"]], "content": m["content"]} for m in result.data]


def _save_message(session_id: str, phase: int, role: str, content: str, audio_meta: dict | None = None) -> None:
    supabase = get_supabase()
    supabase.table("interview_messages").insert(
        {
            "session_id": session_id,
            "phase": phase,
            "role": role,
            "content": content,
            "audio_meta": audio_meta,
        }
    ).execute()


def _questions_for_phase4(candidate: dict) -> list[dict]:
    entries = retrieve_questions(candidate["resume_text"], candidate["field"], k=5)
    return [{"question": e.question, "answer": e.answer} for e in entries]


def _generate_phase_opener(session: dict, candidate: dict) -> str:
    phase = session["current_phase"]
    questions = _questions_for_phase4(candidate) if phase == 4 else None
    system_prompt = build_system_prompt(phase, candidate["resume_sections"], questions)
    return chat_text(system_prompt, "Begin this phase now with your first question.")


def start_session(candidate_id: str) -> dict:
    candidate = _load_candidate(candidate_id)
    supabase = get_supabase()
    result = (
        supabase.table("interview_sessions")
        .insert({"candidate_id": candidate_id, "current_phase": 1, "status": "in_progress"})
        .execute()
    )
    session = result.data[0]

    opener = _generate_phase_opener(session, candidate)
    _save_message(session["id"], phase=1, role="interviewer", content=opener)

    return {"session_id": session["id"], "phase": 1, "message": opener}


def handle_message(session_id: str, content: str) -> dict:
    session = _load_session(session_id)
    candidate = _load_candidate(session["candidate_id"])
    phase = session["current_phase"]

    _save_message(session_id, phase=phase, role="candidate", content=content)

    questions = _questions_for_phase4(candidate) if phase == 4 else None
    system_prompt = build_system_prompt(phase, candidate["resume_sections"], questions)
    history = _load_history(session_id)

    result = chat_json(system_prompt, history, TURN_SCHEMA, "interview_turn")
    reply = result["reply"]
    _save_message(session_id, phase=phase, role="interviewer", content=reply)

    supabase = get_supabase()

    if result["phase_complete"]:
        next_phase = phase + 1
        if next_phase > TOTAL_PHASES:
            supabase.table("interview_sessions").update(
                {"status": "completed", "completed_at": "now()"}
            ).eq("id", session_id).execute()

            from app.evaluation.report import generate_final_report

            generate_final_report(session_id)

            return {"phase": phase, "reply": reply, "status": "completed"}

        supabase.table("interview_sessions").update({"current_phase": next_phase}).eq(
            "id", session_id
        ).execute()
        session["current_phase"] = next_phase
        opener = _generate_phase_opener(session, candidate)
        _save_message(session_id, phase=next_phase, role="interviewer", content=opener)
        reply = f"{reply}\n\n{opener}"
        phase = next_phase

    return {"phase": phase, "reply": reply, "status": "in_progress"}
