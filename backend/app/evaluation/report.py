from app.db.client import get_supabase
from app.evaluation.evaluator import evaluate_phase
from app.llm import chat_text


def generate_final_report(session_id: str) -> dict:
    per_phase_scores: dict[str, float | None] = {}
    notes_by_phase: dict[str, str] = {}

    for phase in range(1, 6):
        result = evaluate_phase(session_id, phase)
        per_phase_scores[str(phase)] = result["score"]
        notes_by_phase[str(phase)] = result["notes"]

    notes_block = "\n".join(f"Phase {p}: {n}" for p, n in notes_by_phase.items())
    summary = chat_text(
        system_prompt=(
            "Write a concise (4-6 sentence) final interview report for a candidate, "
            "based on per-phase evaluator notes. Be direct and specific, not generic."
        ),
        user_prompt=f"Per-phase evaluator notes:\n{notes_block}",
    )

    supabase = get_supabase()
    supabase.table("final_reports").upsert(
        {
            "session_id": session_id,
            "summary": summary,
            "per_phase_scores": per_phase_scores,
        },
        on_conflict="session_id",
    ).execute()

    return {"session_id": session_id, "summary": summary, "per_phase_scores": per_phase_scores}


def get_report(session_id: str) -> dict | None:
    supabase = get_supabase()
    result = (
        supabase.table("final_reports").select("*").eq("session_id", session_id).maybe_single().execute()
    )
    return result.data if result else None
