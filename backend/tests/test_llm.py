from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.llm import chat_json, chat_text


def _fake_response(text: str):
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)])


def test_chat_text_calls_anthropic_and_returns_text():
    fake_client = MagicMock()
    fake_client.messages.create.return_value = _fake_response("hello back")

    with patch("app.llm.get_anthropic_client", return_value=fake_client):
        result = chat_text("system prompt", "hi")

    assert result == "hello back"
    _, kwargs = fake_client.messages.create.call_args
    assert kwargs["system"] == "system prompt"
    assert kwargs["messages"] == [{"role": "user", "content": "hi"}]
    assert kwargs["model"] == "claude-opus-5"
    assert "format" not in kwargs["output_config"]


def test_chat_json_sets_json_schema_format_and_parses_result():
    fake_client = MagicMock()
    fake_client.messages.create.return_value = _fake_response('{"score": 5}')
    schema = {"type": "object", "properties": {"score": {"type": "integer"}}}

    with patch("app.llm.get_anthropic_client", return_value=fake_client):
        result = chat_json("system", [{"role": "user", "content": "grade this"}], schema, "grade")

    assert result == {"score": 5}
    _, kwargs = fake_client.messages.create.call_args
    assert kwargs["output_config"]["format"] == {"type": "json_schema", "schema": schema}
