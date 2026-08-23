from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-5"
    # "high" burns most of the token budget on thinking for a simple conversational
    # turn, truncating the actual JSON reply before it finishes. "medium" leaves
    # enough headroom while still giving the model room to reason about follow-ups.
    anthropic_effort: str = "medium"

    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "tAtHhBlA3E0eKZJKNSKE"
    elevenlabs_stt_model: str = "scribe_v2"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_management_token: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
