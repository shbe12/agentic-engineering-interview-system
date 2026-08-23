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
    # "Daniel" — premade voice, works on the free tier. The spec's original voice
    # (tAtHhBlA3E0eKZJKNSKE, "Margot") is a Professional Voice Clone, which free
    # tier can't use via the API at all (HTTP 402), regardless of "My Voices" slots.
    elevenlabs_voice_id: str = "onwK4e9ZLuTAKqWW03F9"
    elevenlabs_stt_model: str = "scribe_v2"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_management_token: str = ""

    # Comma-separated list of allowed frontend origins for CORS. Defaults to the
    # local Vite dev server; set to the deployed frontend's URL in production.
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
