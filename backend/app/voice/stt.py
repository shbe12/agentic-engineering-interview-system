"""Speech-to-text via ElevenLabs Scribe. Note: the original spec text says "OpenAI
whisper model, which is text-to-speech" — that's incorrect (Whisper is speech-to-text,
and this project uses Claude, not OpenAI, for its LLM anyway). Claude has no
speech-to-text capability, so voice transcription runs on ElevenLabs Scribe instead —
text-to-speech (the interviewer's voice) is also ElevenLabs, in tts.py.
"""

from app.config import get_settings
from app.voice.client import get_elevenlabs_client


def transcribe(file_path: str) -> dict:
    """Returns {"text": str, "duration_seconds": float, "word_count": int}."""
    settings = get_settings()
    with open(file_path, "rb") as f:
        result = get_elevenlabs_client().speech_to_text.convert(
            model_id=settings.elevenlabs_stt_model, file=f
        )

    text = result.text
    duration = result.audio_duration_secs or 0.0
    word_count = sum(1 for w in result.words if w.type == "word")

    return {"text": text, "duration_seconds": float(duration), "word_count": word_count}
