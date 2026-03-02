"""FastAPI Annotated dependency providers."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated
from urllib.parse import urlparse

from arq import ArqRedis, create_pool
from arq.connections import RedisSettings
from fastapi import Depends, Header, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.db import get_session


# ─── Redis / Arq ─────────────────────────────────────────────────────────────


def _parse_redis_url(url: str) -> RedisSettings:
    parsed = urlparse(url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        password=parsed.password,
        database=int(parsed.path.lstrip("/") or 0),
    )


redis_settings = _parse_redis_url(settings.redis_url)


async def get_redis_pool(request: Request) -> ArqRedis:
    pool: ArqRedis | None = getattr(request.app.state, "redis_pool", None)
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis pool not initialized",
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

RedisPool = Annotated[ArqRedis, Depends(get_redis_pool)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
TenantId = Annotated[str, Depends(get_current_tenant)]
UserId = Annotated[str, Depends(get_current_user_id)]
