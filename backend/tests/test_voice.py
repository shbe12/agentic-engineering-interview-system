from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.voice.anxiety import detect_anxiety
from app.voice.stt import transcribe
from app.voice.tts import synthesize


def test_detect_anxiety_flags_fast_speech():
    result = detect_anxiety("a normal length answer with words in it", duration_seconds=5, word_count=20)
    assert result["anxious"] is True
    assert "fast speech" in result["reason"]


def test_detect_anxiety_ignores_calm_speech():
    result = detect_anxiety(
        "a calm and steady answer with normal pacing throughout", duration_seconds=15, word_count=20
    )
    assert result["anxious"] is False
    assert result["reason"] == ""


def test_detect_anxiety_flags_disfluent_speech():
    result = detect_anxiety(
        "um um uh I I think the the answer is uh gradient descent", duration_seconds=20, word_count=20
    )
    assert result["anxious"] is True
    assert "stuttering" in result["reason"]


def test_transcribe_calls_whisper_and_parses_result(tmp_path):
    audio_file = tmp_path / "answer.webm"
    audio_file.write_bytes(b"fake audio bytes")

    fake_result = SimpleNamespace(
        text="hello there",
        duration=4.0,
        words=[{"word": "hello"}, {"word": "there"}],
    )
    fake_client = MagicMock()
    fake_client.audio.transcriptions.create.return_value = fake_result

    with patch("app.voice.stt.get_openai_client", return_value=fake_client):
        result = transcribe(str(audio_file))

    assert result == {"text": "hello there", "duration_seconds": 4.0, "word_count": 2}
    _, kwargs = fake_client.audio.transcriptions.create.call_args
    assert kwargs["model"] == "whisper-1"
    assert kwargs["response_format"] == "verbose_json"


def test_synthesize_calls_elevenlabs_with_configured_voice():
    fake_client = MagicMock()
    fake_client.text_to_speech.convert.return_value = [b"chunk1", b"chunk2"]

    with patch("app.voice.tts._client", return_value=fake_client):
        audio = synthesize("Hello, candidate.")

    assert audio == b"chunk1chunk2"
    _, kwargs = fake_client.text_to_speech.convert.call_args
    assert kwargs["voice_id"] == "tAtHhBlA3E0eKZJKNSKE"
    assert kwargs["text"] == "Hello, candidate."
