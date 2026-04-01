from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "Gr8hub — Personal Development Platform"
    environment: str = "development"
    debug: bool = False  # SECURITY: Never default to True

    # Database — REQUIRED, no default (prevents accidental hardcoded credentials)
    database_url: str

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Qdrant
    qdrant_url: str = "http://qdrant:6333"

    # Security — REQUIRED, no default (prevents insecure fallback)
    secret_key: str
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    algorithm: str = "HS256"

    # Anthropic
    anthropic_api_key: str = ""

    # Token System — REQUIRED, no default
    token_hmac_secret: str

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
