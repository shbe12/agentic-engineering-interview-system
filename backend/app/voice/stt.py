"""Speech-to-text via OpenAI Whisper. Note: the original spec text says "OpenAI whisper
model, which is text-to-speech" — that's incorrect, Whisper is speech-to-text. This module
implements it correctly: candidate's spoken answer (audio) -> text. Text-to-speech (the
interviewer's voice) is ElevenLabs, in tts.py.
"""

from app.llm import get_openai_client


def transcribe(file_path: str) -> dict:
    """Returns {"text": str, "duration_seconds": float, "word_count": int}."""
    client = get_openai_client()
    with open(file_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )

    text = result.text
    duration = getattr(result, "duration", None) or 0.0
    words = getattr(result, "words", None) or []
    word_count = len(words) if words else len(text.split())

    return {"text": text, "duration_seconds": float(duration), "word_count": word_count}
