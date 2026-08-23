from unittest.mock import patch

from app.evaluation import evaluator


def test_phase_1_has_no_evaluation(fake_supabase):
    result = evaluator.evaluate_phase("session-1", 1)

    assert result["score"] is None
    assert "phase 1" in result["notes"].lower()
    saved = fake_supabase.rows["phase_evaluations"][0]
    assert saved["phase"] == 1
    assert saved["score"] is None


def test_phase_with_no_transcript_is_not_reached(fake_supabase):
    result = evaluator.evaluate_phase("session-1", 3)

    assert result["score"] is None
    assert "not reached" in result["notes"].lower()


def test_phase_2_uses_llm_judge_over_transcript(fake_supabase):
    fake_supabase.table("interview_messages").insert(
        {"session_id": "session-1", "phase": 2, "role": "interviewer", "content": "Tell me about your RAG project."}
    ).execute()
    fake_supabase.table("interview_messages").insert(
        {"session_id": "session-1", "phase": 2, "role": "candidate", "content": "It retrieves chunks then generates."}
    ).execute()

    with patch(
        "app.evaluation.evaluator.chat_json",
        return_value={"score": 72, "notes": "Went 3 levels deep before getting stuck."},
    ) as mock_judge:
        result = evaluator.evaluate_phase("session-1", 2)

    mock_judge.assert_called_once()
    assert result["score"] == 72
    saved = fake_supabase.rows["phase_evaluations"][0]
    assert saved["score"] == 72
    assert saved["phase"] == 2
