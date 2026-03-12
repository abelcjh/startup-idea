from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings


def _env_files() -> list[Path]:
    """Find .env files: local .env first, then repo root .env."""
    files: list[Path] = []
    for base in [Path(__file__).resolve().parent, Path.cwd()]:
        if (base / ".env").exists():
            files.append(base / ".env")
            break
    root = Path(__file__).resolve().parents[3]  # apps/api/app -> repo root
    if (root / ".env").exists():
        files.append(root / ".env")
    return files


class Settings(BaseSettings):
    app_version: str = "0.1.0"

    database_url: str = "http://localhost:54321"
    supabase_secret_key: str = ""
    direct_url: str = "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"

    redis_url: str = "redis://localhost:6379"

    litellm_proxy_url: str = "http://localhost:4000"
    mistral_api_key: str = ""

    cors_origins: list[str] = ["http://localhost:3000"]

    sentry_dsn: str = ""

    model_config = {"env_file": _env_files(), "env_file_encoding": "utf-8", "extra": "ignore"}

    @model_validator(mode="after")
    def _fix_direct_url(self) -> "Settings":
        """Ensure the asyncpg driver prefix is present for SQLAlchemy."""
        url = self.direct_url
        if url.startswith("postgresql://"):
            self.direct_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            self.direct_url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return self

settings = Settings()
