"""
Discovery endpoints — enqueue LangGraph runs and poll for results.

POST /discovery/runs      → 202 Accepted (enqueues Arq job)
GET  /discovery/runs      → list recent runs for tenant
GET  /discovery/runs/{id} → poll single run status + payload
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, HTTPException, status

from app.dependencies import DbSession, RedisPool, TenantId, UserId
from app.schemas.requests import (
    DiscoveryEnqueueRequest,
    DiscoveryEnqueueResponse,
    DiscoveryRunResponse,
)
from app.services import agent_runs as svc

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/discovery", tags=["discovery"])


# ── POST /discovery/runs ─────────────────────────────────────────────────────


@router.post(
    "/runs",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=DiscoveryEnqueueResponse,
)
async def enqueue_discovery(
    body: DiscoveryEnqueueRequest,
    redis: RedisPool,
    db: DbSession,
    tenant_id: TenantId,
    user_id: UserId,
) -> DiscoveryEnqueueResponse:
    log = logger.bind(tenant_id=tenant_id)

    run = await svc.create_queued_run(
        db,
        organization_id=uuid.UUID(tenant_id),
        triggered_by_id=uuid.UUID(user_id),
        input_payload={"interview_ids": body.interview_ids},
    )
    log.info("discovery.enqueued", run_id=str(run.id))

    await redis.enqueue_job(
        "run_product_discovery",
        str(run.organization_id),
        str(run.id),
        body.interview_ids,
    )

    return DiscoveryEnqueueResponse(
        run_id=str(run.id),
        status=run.status,
    )


# ── GET /discovery/runs ──────────────────────────────────────────────────────


@router.get("/runs", response_model=list[DiscoveryRunResponse])
async def list_runs(
    db: DbSession,
    tenant_id: TenantId,
) -> list[DiscoveryRunResponse]:
    runs = await svc.list_runs_for_org(db, uuid.UUID(tenant_id))
    return [
        DiscoveryRunResponse(
            run_id=r.id,
            status=r.status,
            graph_name=r.graph_name,
            token_usage=r.token_usage,
            output_payload=r.output_payload,
            error_message=r.error_message,
            started_at=r.started_at,
            completed_at=r.completed_at,
            created_at=r.created_at,
        )
        for r in runs
    ]


# ── GET /discovery/runs/{run_id} ─────────────────────────────────────────────


@router.get("/runs/{run_id}", response_model=DiscoveryRunResponse)
async def get_run(
    run_id: uuid.UUID,
    db: DbSession,
    tenant_id: TenantId,
) -> DiscoveryRunResponse:
    run = await svc.get_run(db, run_id)
    if run is None or str(run.organization_id) != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    return DiscoveryRunResponse(
        run_id=run.id,
        status=run.status,
        graph_name=run.graph_name,
        token_usage=run.token_usage,
        output_payload=run.output_payload,
        error_message=run.error_message,
        started_at=run.started_at,
        completed_at=run.completed_at,
        created_at=run.created_at,
    )
