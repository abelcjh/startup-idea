"""
Arq worker — executes ProductDiscoveryGraph jobs off the Redis queue.

Start with:  arq app.worker.WorkerSettings
"""

from __future__ import annotations

import traceback
import uuid
from typing import Any

import structlog
from sqlmodel.ext.asyncio.session import AsyncSession

from app.agents.graph import product_discovery_graph
from app.db import engine
from app.dependencies import redis_settings
from app.services import agent_runs as svc

logger = structlog.get_logger(__name__)


async def _get_session() -> AsyncSession:
    return AsyncSession(engine)


async def _fetch_interview_texts(
    session: AsyncSession,
    interview_ids: list[str],
) -> list[str]:
    """Fetch raw transcript text for given interview UUIDs.

    Uses raw SQL against the `interviews` table written by Prisma / Airbyte.
    """
    from sqlalchemy import text

    rows = await session.exec(  # type: ignore[call-overload]
        text("SELECT transcript FROM interviews WHERE id = ANY(:ids) AND deleted_at IS NULL"),
        params={"ids": [uuid.UUID(i) for i in interview_ids]},
    )
    return [row[0] for row in rows]  # type: ignore[index]


# ─── Task function ───────────────────────────────────────────────────────────


async def run_product_discovery(
    ctx: dict[str, Any],
    organization_id: str,
    run_id: str,
    interview_ids: list[str],
) -> None:
    log = logger.bind(tenant_id=organization_id, run_id=run_id)
    log.info("worker.discovery.start", interview_count=len(interview_ids))

    session = await _get_session()
    rid = uuid.UUID(run_id)

    try:
        await svc.mark_running(session, rid)

        transcripts = await _fetch_interview_texts(session, interview_ids)
        if not transcripts:
            await svc.mark_failed(session, rid, error_message="No interviews found for given IDs")
            log.warning("worker.discovery.no_interviews")
            return

        result = await product_discovery_graph.ainvoke({
            "organization_id": organization_id,
            "run_id": run_id,
            "raw_interviews": transcripts,
        })

        if result.get("errors"):
            error_msg = "; ".join(result["errors"])
            await svc.mark_failed(session, rid, error_message=error_msg)
            log.error("worker.discovery.graph_errors", errors=result["errors"])
            return

        payload = result["handoff_payload"]
        await svc.mark_completed(
            session,
            rid,
            output_payload=payload.model_dump(mode="json"),
            token_usage=payload.total_token_usage,
        )
        log.info("worker.discovery.done", tokens=payload.total_token_usage)

    except Exception:
        tb = traceback.format_exc()
        await svc.mark_failed(session, rid, error_message=tb[-2000:])
        log.error("worker.discovery.exception", exc_info=True)

    finally:
        await session.close()


# ─── Arq WorkerSettings ─────────────────────────────────────────────────────


class WorkerSettings:
    """Arq worker config. Start: `arq app.worker.WorkerSettings`"""

    redis_settings = redis_settings
    functions = [run_product_discovery]
    max_jobs = 5
    job_timeout = 600  # 10min per graph run
    poll_delay = 0.5
