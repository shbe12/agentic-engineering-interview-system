from functools import lru_cache

from elevenlabs.client import ElevenLabs

from app.config import get_settings


@lru_cache
def get_elevenlabs_client() -> ElevenLabs:
    settings = get_settings()
    return ElevenLabs(api_key=settings.elevenlabs_api_key)
