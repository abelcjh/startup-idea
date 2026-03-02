from pydantic_settings import BaseSettings
from pydantic import model_validator


class Settings(BaseSettings):
    app_version: str = "0.1.0"

    supabase_url: str = "http://localhost:54321"
    supabase_service_role_key: str = ""
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"

    redis_url: str = "redis://localhost:6379"

    litellm_proxy_url: str = "http://localhost:4000"
    mistral_api_key: str = ""

    cors_origins: list[str] = ["http://localhost:3000"]

    sentry_dsn: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @model_validator(mode="after")
    def _fix_database_url(self) -> "Settings":
        """Ensure the asyncpg driver prefix is present for SQLAlchemy."""
        url = self.database_url
        if url.startswith("postgresql://"):
            self.database_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            self.database_url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return self

settings = Settings()
