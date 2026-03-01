"""
Interview ingestion endpoints — SOC2-compliant PII scrub + vectorisation.

POST /interviews       → ingest single interview (201)
POST /interviews/batch → ingest up to 50 interviews (201)
GET  /interviews       → list interviews for tenant
GET  /interviews/{id}  → single interview detail
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import text

from app.dependencies import DbSession, TenantId
from app.schemas.requests import (
    IngestBatchRequest,
    IngestBatchResponse,
    IngestInterviewRequest,
    IngestInterviewResponse,
    InterviewListItem,
)
from app.services.ingestion import ingest_batch, ingest_interview

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/interviews", tags=["ingestion"])


# ── POST /interviews ─────────────────────────────────────────────────────────


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=IngestInterviewResponse,
)
async def create_interview(
    body: IngestInterviewRequest,
    db: DbSession,
    tenant_id: TenantId,
) -> IngestInterviewResponse:
    log = logger.bind(tenant_id=tenant_id)
    log.info("interviews.ingest.start", source=body.source_name)

    result = await ingest_interview(
        db,
        organization_id=tenant_id,
        source_name=body.source_name,
        transcript=body.transcript,
        contact_name=body.contact_name,
        source_ref=body.source_ref,
        language=body.language,
        data_source_id=body.data_source_id,
    )

    log.info("interviews.ingest.done", interview_id=str(result.interview_id))
    return IngestInterviewResponse(
        interview_id=result.interview_id,
        pii_entities_found=result.pii_entities_found,
        embedding_dim=result.embedding_dim,
    )


# ── POST /interviews/batch ───────────────────────────────────────────────────


@router.post(
    "/batch",
    status_code=status.HTTP_201_CREATED,
    response_model=IngestBatchResponse,
)
async def create_interviews_batch(
    body: IngestBatchRequest,
    db: DbSession,
    tenant_id: TenantId,
) -> IngestBatchResponse:
    log = logger.bind(tenant_id=tenant_id)
    log.info("interviews.batch.start", count=len(body.transcripts))

    results = await ingest_batch(
        db,
        organization_id=tenant_id,
        source_name=body.source_name,
        transcripts=body.transcripts,
        language=body.language,
        data_source_id=body.data_source_id,
    )

    log.info("interviews.batch.done", count=len(results))
    return IngestBatchResponse(
        count=len(results),
        interview_ids=[r.interview_id for r in results],
        total_pii_entities=sum(r.pii_entities_found for r in results),
    )


# ── GET /interviews ──────────────────────────────────────────────────────────


@router.get("", response_model=list[InterviewListItem])
async def list_interviews(
    db: DbSession,
    tenant_id: TenantId,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[InterviewListItem]:
    rows = await db.exec(  # type: ignore[call-overload]
        text("""
            SELECT id, source_ref, contact_name, sentiment, language, created_at
            FROM interviews
            WHERE organization_id = :org_id AND deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT :lim OFFSET :off
        """),
        params={"org_id": uuid.UUID(tenant_id), "lim": limit, "off": offset},
    )
    return [
        InterviewListItem(
            id=row[0], source_ref=row[1], contact_name=row[2],
            sentiment=row[3], language=row[4], created_at=row[5],
        )
        for row in rows
    ]


# ── GET /interviews/{interview_id} ───────────────────────────────────────────


@router.get("/{interview_id}")
async def get_interview(
    interview_id: uuid.UUID,
    db: DbSession,
    tenant_id: TenantId,
) -> dict:
    rows = await db.exec(  # type: ignore[call-overload]
        text("""
            SELECT id, organization_id, source_ref, contact_name,
                   transcript, summary, sentiment, language, created_at
            FROM interviews
            WHERE id = :iid AND deleted_at IS NULL
        """),
        params={"iid": interview_id},
    )
    row = rows.first()
    if row is None or str(row[1]) != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    return {
        "id": str(row[0]),
        "organization_id": str(row[1]),
        "source_ref": row[2],
        "contact_name": row[3],
        "transcript": row[4],
        "summary": row[5],
        "sentiment": row[6],
        "language": row[7],
        "created_at": row[8].isoformat() if row[8] else None,
    }
