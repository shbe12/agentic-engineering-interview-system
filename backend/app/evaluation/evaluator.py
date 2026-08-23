from app.db.client import get_supabase
from app.llm import chat_json

EVAL_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "number"},
        "notes": {"type": "string"},
    },
    "required": ["score", "notes"],
    "additionalProperties": False,
}

PHASE_EVAL_INSTRUCTIONS = {
    2: """Score this phase 0-100 using a "Russian doll" / Socratic depth metric: how many \
levels deep did the candidate successfully answer follow-up questions before getting stuck? \
Deeper = higher score. Also note whether, when a hint was given, the candidate moved toward \
the correct answer afterward — factor that into the score and mention it in notes.""",
    3: """Score this phase 0-100 using the same "Russian doll" / Socratic depth metric as \
phase 2 (how deep the candidate could go on their second project before getting stuck), \
factoring in whether hints (if any) helped them move toward the correct answer.""",
    4: """Score this phase 0-100 as (number of factually correct answers / number of \
questions asked) * 100. Judge correctness against your own ML knowledge, not just \
surface wording. State the count in notes, e.g. "3/5 correct".""",
    5: """Score this phase 0-100 on whether the candidate seemed proactive, visionary, \
realistic/grounded, and a good team player. Apply a meaningful penalty (lower score) if \
the candidate did not ask any follow-up question when given the chance at the end.""",
}


def _load_phase_transcript(session_id: str, phase: int) -> list[dict]:
    supabase = get_supabase()
    result = (
        supabase.table("interview_messages")
        .select("role, content")
        .eq("session_id", session_id)
        .eq("phase", phase)
        .order("created_at")
        .execute()
    )
    role_map = {"interviewer": "assistant", "candidate": "user"}
    return [{"role": role_map[m["role"]], "content": m["content"]} for m in result.data]


def evaluate_phase(session_id: str, phase: int) -> dict:
    if phase == 1:
        result = {"score": None, "notes": "No evaluation for phase 1 — background only."}
    else:
        transcript = _load_phase_transcript(session_id, phase)
        if not transcript:
            result = {"score": None, "notes": "Phase was not reached."}
        else:
            judged = chat_json(
                system_prompt=(
                    "You are grading one phase of a machine learning engineer mock "
                    "interview transcript. " + PHASE_EVAL_INSTRUCTIONS[phase]
                ),
                messages=[
                    {
                        "role": "user",
                        "content": "Transcript:\n"
                        + "\n".join(f"{m['role']}: {m['content']}" for m in transcript),
                    }
                ],
                schema=EVAL_SCHEMA,
                schema_name="phase_eval",
            )
            result = judged

    supabase = get_supabase()
    supabase.table("phase_evaluations").upsert(
        {"session_id": session_id, "phase": phase, **result},
        on_conflict="session_id,phase",
    ).execute()
    return result
