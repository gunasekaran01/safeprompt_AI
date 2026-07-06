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
    SUPABASE_ANON_KEY: str = ""

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

    # ML detector toggles and model names
    ENABLE_ML_DETECTORS: bool = True
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    TOXICITY_MODEL_NAME: str = "original"

    # Toxicity detection thresholds
    TOXICITY_CATEGORY_THRESHOLD: float = 0.5

    # Injection similarity threshold for semantic matching (0-1)
    INJECTION_SIMILARITY_THRESHOLD: float = 0.75

    # Scoring engine weights and floor settings
    SCORE_INJECTION_PENALTY_WEIGHT: float = 0.6
    SCORE_INJECTION_CONFIDENCE_WEIGHT: float = 0.4
    SCORE_TOXICITY_PENALTY_WEIGHT: float = 0.6
    SCORE_TOXICITY_SEVERITY_WEIGHT: float = 0.4

    SCORE_HIGH_CONFIDENCE_FLOOR_THRESHOLD: float = 0.9
    SCORE_HIGH_CONFIDENCE_SCORE_CAP: float = 15.0
    # Directory to write generated reports to (override in tests)
    REPORTS_DIR: str = "reports"

    # Email(s) of accounts that get admin-dashboard access (GET/DELETE
    # /api/admin/...), checked case-insensitively against the logged-in
    # user's email by app/api/deps.py's is_admin_email(). Comma-separated
    # for more than one admin. ADMIN_EMAIL (singular) is kept for
    # backward compatibility and merged into the same list.
    ADMIN_EMAILS: str = ""
    ADMIN_EMAIL: str = "gunavera2020@gmail.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def admin_emails_list(self) -> List[str]:
        """
        Every configured admin email, lowercased and stripped, combining
        ADMIN_EMAILS (comma-separated) and the legacy singular
        ADMIN_EMAIL. This is what app/api/deps.py's is_admin_email()
        actually checks against -- the single source of truth for admin
        access, both for require_admin's 403 enforcement and for the
        is_admin flag GET /api/auth/me returns to the frontend.
        """
        emails = [email.strip().lower() for email in self.ADMIN_EMAILS.split(",") if email.strip()]
        if self.ADMIN_EMAIL.strip():
            emails.append(self.ADMIN_EMAIL.strip().lower())
        return list(dict.fromkeys(emails))  # de-duplicate, preserve order

    @property
    def is_supabase_configured(self) -> bool:
        """Whether both Supabase settings needed to create a client are present."""
        # Accept either a service-role key or an anon/public key for
        # authentication checks; tests set SUPABASE_ANON_KEY rather than
        # a service-role key so permit either to indicate configuration.
        return bool(self.SUPABASE_URL and (self.SUPABASE_KEY or self.SUPABASE_ANON_KEY))


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance so environment parsing only happens
    once per process, while still being easily overridable in tests via
    dependency overrides.
    """
    return Settings()
