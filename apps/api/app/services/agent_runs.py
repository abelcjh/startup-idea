"""AgentRun CRUD — async SQLModel operations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import structlog
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.agent_run import AgentRun, AgentRunStatus

logger = structlog.get_logger(__name__)

GRAPH_NAME = "product_discovery"


async def create_queued_run(
    session: AsyncSession,
    *,
    organization_id: uuid.UUID,
    triggered_by_id: uuid.UUID,
    input_payload: dict,
) -> AgentRun:
    run = AgentRun(
        organization_id=organization_id,
        triggered_by_id=triggered_by_id,
        graph_name=GRAPH_NAME,
        input_payload=input_payload,
        status=AgentRunStatus.QUEUED,
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)
    logger.info(
        "agent_run.created",
        tenant_id=str(organization_id),
        run_id=str(run.id),
    )
    return run


async def mark_running(session: AsyncSession, run_id: uuid.UUID) -> None:
    run = await session.get(AgentRun, run_id)
    if run is None:
        return
    run.status = AgentRunStatus.RUNNING
    run.started_at = datetime.now(timezone.utc)
    session.add(run)
    await session.commit()


async def mark_completed(
    session: AsyncSession,
    run_id: uuid.UUID,
    *,
    output_payload: dict,
    token_usage: int,
) -> None:
    run = await session.get(AgentRun, run_id)
    if run is None:
        return
    run.status = AgentRunStatus.COMPLETED
    run.output_payload = output_payload
    run.token_usage = token_usage
    run.completed_at = datetime.now(timezone.utc)
    session.add(run)
    await session.commit()


async def mark_failed(
    session: AsyncSession,
    run_id: uuid.UUID,
    *,
    error_message: str,
) -> None:
    run = await session.get(AgentRun, run_id)
    if run is None:
        return
    run.status = AgentRunStatus.FAILED
    run.error_message = error_message
    run.completed_at = datetime.now(timezone.utc)
    session.add(run)
    await session.commit()


async def get_run(session: AsyncSession, run_id: uuid.UUID) -> AgentRun | None:
    return await session.get(AgentRun, run_id)


async def list_runs_for_org(
    session: AsyncSession,
    organization_id: uuid.UUID,
    *,
    limit: int = 20,
) -> list[AgentRun]:
    stmt = (
        select(AgentRun)
        .where(AgentRun.organization_id == organization_id)
        .order_by(AgentRun.created_at.desc())  # type: ignore[union-attr]
        .limit(limit)
    )
    results = await session.exec(stmt)
    return list(results.all())
