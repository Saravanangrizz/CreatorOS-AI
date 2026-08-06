"""
Central configuration. All environment-dependent values live here and
nowhere else — routes/services/agents must never read os.environ directly.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CreatorOS AI"
    environment: str = "development"

    # --- Auth ---
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    # --- Database ---
    database_url: str = "sqlite:///./creatoros.db"

    # --- AI provider selection (switchable without code changes) ---
    # one of: "gemini" | "openai" | "claude" | "mock"
    ai_provider: str = "mock"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-latest"

    # --- Demo mode: serves canned responses, no API key required ---
    demo_mode: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
