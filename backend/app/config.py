from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-5.4"
    openai_reasoning_effort: str = "low"

    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "tAtHhBlA3E0eKZJKNSKE"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_management_token: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
