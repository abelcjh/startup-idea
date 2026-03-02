from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import sentry_sdk
import structlog
from arq import create_pool
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import dispose_engine
from app.dependencies import redis_settings
from app.routers.discovery import router as discovery_router
from app.routers.interviews import router as interviews_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if settings.sentry_dsn:
        sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)

    app.state.redis_pool = await create_pool(redis_settings)
    logger.info("startup", version=settings.app_version)

    yield

    await app.state.redis_pool.close()
    await dispose_engine()
    logger.info("shutdown")


app = FastAPI(
    title="ProductOS API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(discovery_router)
app.include_router(interviews_router)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


# Mount MCP SSE server at /mcp
from app.mcp.server import mcp_app  # noqa: E402

app.mount("/mcp", mcp_app)
