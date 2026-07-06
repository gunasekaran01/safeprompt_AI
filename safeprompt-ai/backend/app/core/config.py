"""
Application configuration.

Centralizes all environment-driven settings so the rest of the backend
never reads os.environ directly. Values can be overridden via a .env file
in the backend/ directory (see .env.example).
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General application metadata
    APP_NAME: str = "SafePrompt AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS: origins allowed to call the API from the browser
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Supabase project connection. SUPABASE_KEY should be the *service
    # role* key for backend use (never expose it to the frontend, which
    # uses its own anon key via VITE_SUPABASE_ANON_KEY instead).
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # When True (the default), app data (analyses/reports/profiles) is
    # stored in an in-memory local store inside this process instead of
    # Supabase's Postgres tables (see app/db/local_store.py) -- so the
    # backend never needs the Supabase *service role* secret. Auth still
    # goes through the real Supabase project using SUPABASE_URL/KEY (the
    # anon/public key is fine for that). Data does NOT survive a server
    # restart in this mode. Set to False once you have a real service-role
    # key and want data to persist in Supabase.
    USE_LOCAL_DATA_STORE: bool = True

    # Safety score thresholds (0-100 scale) used by the scoring engine.
    # Defined here so they are configurable without touching business logic.
    RISK_THRESHOLD_SAFE: int = 90
    RISK_THRESHOLD_LOW: int = 75
    RISK_THRESHOLD_MEDIUM: int = 50
    RISK_THRESHOLD_HIGH: int = 25
    # Anything below RISK_THRESHOLD_HIGH is classified as "Critical"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def is_supabase_configured(self) -> bool:
        """Whether both Supabase settings needed to create a client are present."""
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance so environment parsing only happens
    once per process, while still being easily overridable in tests via
    dependency overrides.
    """
    return Settings()
