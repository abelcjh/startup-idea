"""FastAPI Annotated dependency providers."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Annotated, Any
from urllib.parse import urlparse

from fastapi import Depends, Header, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

if TYPE_CHECKING:
    from arq import ArqRedis
    from arq.connections import RedisSettings

from app.config import settings
from app.db import get_session


# ─── Redis / Arq ─────────────────────────────────────────────────────────────


def _parse_redis_url(url: str) -> RedisSettings:
    from arq.connections import RedisSettings

    parsed = urlparse(url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        password=parsed.password,
        database=int(parsed.path.lstrip("/") or 0),
    )


redis_settings: RedisSettings | None = (
    _parse_redis_url(settings.redis_url) if settings.redis_url else None
)


async def get_redis_pool(request: Request):  # noqa: ANN201
    from arq import ArqRedis

    pool: ArqRedis | None = getattr(request.app.state, "redis_pool", None)
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis not available — start Redis or Docker to enable async job queue",
        )
    return pool


# ─── Database ────────────────────────────────────────────────────────────────


async def get_db() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


# ─── Tenant Extraction (placeholder — wire to Unkey / WorkOS) ────────────────


async def get_current_tenant(
    x_organization_id: Annotated[str, Header(description="Tenant UUID from auth layer")],
) -> str:
    if not x_organization_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Organization-Id header",
        )
    return x_organization_id


async def get_current_user_id(
    x_user_id: Annotated[str, Header(description="User UUID from auth layer")],
) -> str:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )
    return x_user_id


# ─── Annotated type aliases (import these in routers) ────────────────────────

RedisPool = Annotated[Any, Depends(get_redis_pool)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
TenantId = Annotated[str, Depends(get_current_tenant)]
UserId = Annotated[str, Depends(get_current_user_id)]
