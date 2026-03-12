"""Async SQLModel engine and session factory."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from app.config import settings

engine = create_async_engine(
    settings.direct_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
)


async def get_session() -> AsyncIterator[SQLModelAsyncSession]:
    async with SQLModelAsyncSession(engine) as session:
        yield session


async def dispose_engine() -> None:
    await engine.dispose()
