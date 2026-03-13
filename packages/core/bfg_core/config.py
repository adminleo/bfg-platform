from pydantic_settings import BaseSettings


class CoreSettings(BaseSettings):
    """Base settings shared across all BFG products.
    Products should subclass this and add their own settings."""

    # App
    app_name: str = "BFG Platform"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://bfg:bfg_dev_2024@db:5432/bfg"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Qdrant
    qdrant_url: str = "http://qdrant:6333"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    algorithm: str = "HS256"

    # AI Providers
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    llm_mode: str = "cloud"  # cloud | ollama | hybrid

    # Token System
    token_hmac_secret: str = "token-hmac-secret-change-in-production"

    # Email
    ses_region: str = "eu-central-1"
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    email_from: str = "noreply@bfg-platform.de"

    # Stripe Payment
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    frontend_url: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "extra": "ignore"}
