from unittest.mock import patch

from app.interview import orchestrator


def _seed_candidate(fake_supabase):
    fake_supabase.table("candidates").insert(
        {
            "id": "cand-1",
            "name": "Ada",
            "resume_text": "Built a RAG project.",
            "resume_sections": {
                "name": "Ada",
                "summary": "ML engineer",
                "education": "",
                "skills": [],
                "experience": [],
                "projects": ["RAG project"],
            },
            "field": "nlp",
        }
    ).execute()


def test_start_session_creates_session_and_opening_message(fake_supabase):
    _seed_candidate(fake_supabase)

    with patch("app.interview.orchestrator.chat_text", return_value="Tell me about yourself."):
        result = orchestrator.start_session("cand-1")

    assert result["phase"] == 1
    assert result["message"] == "Tell me about yourself."
    messages = fake_supabase.rows["interview_messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "interviewer"
    assert messages[0]["phase"] == 1


def test_handle_message_stays_in_phase_when_not_complete(fake_supabase):
    _seed_candidate(fake_supabase)
    session = (
        fake_supabase.table("interview_sessions")
        .insert({"candidate_id": "cand-1", "current_phase": 1, "status": "in_progress"})
        .execute()
        .data[0]
    )

    with patch(
        "app.interview.orchestrator.chat_json",
        return_value={"reply": "Go on...", "phase_complete": False, "hint_given": False},
    ):
        result = orchestrator.handle_message(session["id"], "I'm a student.")

    assert result["status"] == "in_progress"
    assert result["phase"] == 1
    updated = fake_supabase.rows["interview_sessions"][0]
    assert updated["current_phase"] == 1


def test_handle_message_advances_phase_when_complete(fake_supabase):
    _seed_candidate(fake_supabase)
    session = (
        fake_supabase.table("interview_sessions")
        .insert({"candidate_id": "cand-1", "current_phase": 1, "status": "in_progress"})
        .execute()
        .data[0]
    )

    with (
        patch(
            "app.interview.orchestrator.chat_json",
            return_value={"reply": "Great, moving on.", "phase_complete": True, "hint_given": False},
        ),
        patch("app.interview.orchestrator.chat_text", return_value="Let's discuss your project."),
    ):
        result = orchestrator.handle_message(session["id"], "That's my background.")

    assert result["status"] == "in_progress"
    assert result["phase"] == 2
    updated = fake_supabase.rows["interview_sessions"][0]
    assert updated["current_phase"] == 2


def test_handle_message_completes_session_after_phase_5(fake_supabase):
    _seed_candidate(fake_supabase)
    session = (
        fake_supabase.table("interview_sessions")
        .insert({"candidate_id": "cand-1", "current_phase": 5, "status": "in_progress"})
        .execute()
        .data[0]
    )

    with (
        patch(
            "app.interview.orchestrator.chat_json",
            return_value={"reply": "Thanks, that's all.", "phase_complete": True, "hint_given": False},
        ),
        patch("app.evaluation.report.generate_final_report") as gen_report,
    ):
        result = orchestrator.handle_message(session["id"], "No questions for you.")

    assert result["status"] == "completed"
    updated = fake_supabase.rows["interview_sessions"][0]
    assert updated["status"] == "completed"
    gen_report.assert_called_once_with(session["id"])
