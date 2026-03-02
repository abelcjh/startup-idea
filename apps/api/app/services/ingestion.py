"""
Interview ingestion pipeline: PII scrub → vector embedding → DB insert.

Embedding: LiteLLM → mistral-embed (1024 dims) routed through the proxy.
Storage: Raw SQL INSERT into Prisma-managed `interviews` table with pgvector.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import litellm
import structlog
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services import pii

logger = structlog.get_logger(__name__)

EMBED_MODEL = "mistral/mistral-embed"
EMBED_DIM = 1024


@dataclass(frozen=True, slots=True)
class IngestResult:
    interview_id: uuid.UUID
    pii_entities_found: int
    embedding_dim: int


async def _generate_embedding(scrubbed_text: str) -> list[float]:
    response = await litellm.aembedding(model=EMBED_MODEL, input=[scrubbed_text])
    vector: list[float] = response.data[0]["embedding"]
    if len(vector) != EMBED_DIM:
        logger.warning("embedding.dim_mismatch", expected=EMBED_DIM, got=len(vector))
    return vector


async def ingest_interview(
    session: AsyncSession,
    *,
    organization_id: str,
    source_name: str,
    transcript: str,
    contact_name: str | None = None,
    source_ref: str | None = None,
    language: str = "en",
    data_source_id: str | None = None,
) -> IngestResult:
    log = logger.bind(tenant_id=organization_id)

    # 1. PII analysis + scrub
    pii_results = pii.analyze(transcript, language=language)
    scrubbed_transcript = pii.scrub(transcript, language=language, tenant_id=organization_id)
    scrubbed_contact = pii.scrub(contact_name, tenant_id=organization_id) if contact_name else None

    log.info(
        "ingestion.pii_scrubbed",
        pii_entities=len(pii_results),
        transcript_len=len(scrubbed_transcript),
    )

    # 2. Generate vector embedding of scrubbed text
    embedding = await _generate_embedding(scrubbed_transcript)
    log.info("ingestion.embedded", dim=len(embedding))

    # 3. Insert into `interviews` table (Prisma-managed, pgvector column)
    interview_id = uuid.uuid4()
    await session.exec(  # type: ignore[call-overload]
        text("""
            INSERT INTO interviews (
                id, organization_id, data_source_id, source_ref,
                contact_name, transcript, language, embedding,
                created_at, updated_at
            ) VALUES (
                :id, :org_id, :ds_id, :source_ref,
                :contact, :transcript, :lang, :embedding::vector,
                NOW(), NOW()
            )
        """),
        params={
            "id": interview_id,
            "org_id": uuid.UUID(organization_id),
            "ds_id": uuid.UUID(data_source_id) if data_source_id else None,
            "source_ref": source_ref,
            "contact": scrubbed_contact,
            "transcript": scrubbed_transcript,
            "lang": language,
            "embedding": str(embedding),
        },
    )
    await session.commit()

    log.info("ingestion.stored", interview_id=str(interview_id))

    return IngestResult(
        interview_id=interview_id,
        pii_entities_found=len(pii_results),
        embedding_dim=len(embedding),
    )


async def ingest_batch(
    session: AsyncSession,
    *,
    organization_id: str,
    source_name: str,
    transcripts: list[str],
    language: str = "en",
    data_source_id: str | None = None,
) -> list[IngestResult]:
    log = logger.bind(tenant_id=organization_id)
    log.info("ingestion.batch_start", count=len(transcripts))

    results: list[IngestResult] = []
    for transcript in transcripts:
        result = await ingest_interview(
            session,
            organization_id=organization_id,
            source_name=source_name,
            transcript=transcript,
            language=language,
            data_source_id=data_source_id,
        )
        results.append(result)

    log.info(
        "ingestion.batch_done",
        count=len(results),
        total_pii=sum(r.pii_entities_found for r in results),
    )
    return results
