"""Text-to-speech via ElevenLabs, using the candidate-cloned voice from the spec
(voice ID tAtHhBlA3E0eKZJKNSKE, "Margot")."""

from app.config import get_settings
from app.voice.client import get_elevenlabs_client


def synthesize(text: str) -> bytes:
    settings = get_settings()
    audio_chunks = get_elevenlabs_client().text_to_speech.convert(
        voice_id=settings.elevenlabs_voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    return b"".join(audio_chunks)
