from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings


def _find_env_files() -> list[Path]:
    """Locate .env files: local .env first, then walk up to repo root for .env.local."""
    files: list[Path] = []
    local = Path(".env")
    if local.exists():
        files.append(local)

    search = Path(__file__).resolve().parent
    for _ in range(6):
        search = search.parent
        candidate = search / ".env.local"
        if candidate.exists():
            files.append(candidate)
            break
    return files


class Settings(BaseSettings):
    app_version: str = "0.1.0"

    supabase_url: str = "http://localhost:54321"
    supabase_service_role_key: str = ""
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"

    redis_url: str = ""

    litellm_proxy_url: str = "http://localhost:4000"
    mistral_api_key: str = ""

    cors_origins: list[str] = ["http://localhost:3000"]

    sentry_dsn: str = ""

    model_config = {
        "env_file": _find_env_files(),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

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
