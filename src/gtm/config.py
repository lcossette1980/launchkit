"""Application configuration via Pydantic Settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application configuration, loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Database ---
    database_url: str = "postgresql://gtm_user:password@localhost:5432/gtm_analysis"
    redis_url: str = "redis://localhost:6379"

    # --- Storage (S3 / MinIO) ---
    s3_bucket: str = "gtm-analysis"
    aws_endpoint_url: str | None = None
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"

    # --- LLM ---
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: str = "openai"  # "openai" or "anthropic"
    default_model: str = "gpt-4.1-mini"

    # Per-role model overrides — keys must match agent role names
    role_models: dict[str, str] = {
        "orchestrator": "gpt-4.1-mini",
        "analyst": "gpt-4.1-mini",
        "writer": "gpt-4.1-mini",
        "researcher": "gpt-4.1-mini",
        "critic": "gpt-4.1-mini",
    }

    # Token limits
    max_tokens_analysis: int = 8000
    max_tokens_generation: int = 8000
    max_tokens_summary: int = 4096

    # --- Search APIs ---
    serp_api_key: str = ""
    ahrefs_api_key: str = ""
    similarweb_api_key: str = ""

    # --- Application ---
    secret_key: str = "change-me-in-production"
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]
    app_url: str = "http://localhost:8001"

    # --- Auth ---
    magic_link_expiry_minutes: int = 15
    session_expiry_days: int = 30

    # --- Email (empty smtp_host = console logging) ---
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "hello@vclaunchkit.com"

    # --- Stripe ---
    stripe_api_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""
    stripe_agency_price_id: str = ""

    # --- Monitoring ---
    sentry_dsn: str = ""
    metrics_port: int = 9090

    # --- Analysis defaults ---
    default_max_pages: int = 50
    default_max_competitors: int = 5
    analysis_timeout_seconds: int = 900


def get_settings() -> Settings:
    """Singleton-ish factory cached by FastAPI's Depends."""
    return Settings()
