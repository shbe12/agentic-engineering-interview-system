"""Text-to-speech via ElevenLabs, using the candidate-cloned voice from the spec
(voice ID tAtHhBlA3E0eKZJKNSKE, "Margot")."""

from functools import lru_cache

from elevenlabs.client import ElevenLabs

from app.config import get_settings


@lru_cache
def _client() -> ElevenLabs:
    settings = get_settings()
    return ElevenLabs(api_key=settings.elevenlabs_api_key)


def synthesize(text: str) -> bytes:
    settings = get_settings()
    audio_chunks = _client().text_to_speech.convert(
        voice_id=settings.elevenlabs_voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    return b"".join(audio_chunks)
