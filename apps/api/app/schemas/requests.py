"""API request/response schemas for discovery and ingestion endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.agent_run import AgentRunStatus


# ─── Discovery ───────────────────────────────────────────────────────────────


class DiscoveryEnqueueRequest(BaseModel):
    interview_ids: list[str] = Field(
        ..., min_length=1, description="UUIDs of Interview rows to process"
    )


class DiscoveryEnqueueResponse(BaseModel):
    run_id: str = Field(..., description="AgentRun UUID — poll GET /discovery/runs/{run_id}")
    status: AgentRunStatus


class DiscoveryRunResponse(BaseModel):
    run_id: uuid.UUID
    status: AgentRunStatus
    graph_name: str
    token_usage: int
    output_payload: dict | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


# ─── Interview Ingestion ─────────────────────────────────────────────────────


class IngestInterviewRequest(BaseModel):
    source_name: str = Field(..., description="Data source label, e.g. 'Zendesk', 'Zoom'")
    transcript: str = Field(..., min_length=1, description="Raw interview transcript")
    contact_name: str | None = Field(default=None, description="Interviewee name (will be scrubbed)")
    source_ref: str | None = Field(default=None, description="External ID in source system")
    language: str = Field(default="en", max_length=5, description="ISO 639-1 language code")
    data_source_id: str | None = Field(default=None, description="DataSource UUID if linked")


class IngestInterviewResponse(BaseModel):
    interview_id: uuid.UUID
    pii_entities_found: int
    embedding_dim: int
    status: str = "ingested"


class IngestBatchRequest(BaseModel):
    source_name: str = Field(..., description="Data source label")
    transcripts: list[str] = Field(..., min_length=1, max_length=50, description="Raw transcripts")
    language: str = Field(default="en", max_length=5)
    data_source_id: str | None = Field(default=None)


class IngestBatchResponse(BaseModel):
    count: int
    interview_ids: list[uuid.UUID]
    total_pii_entities: int
    status: str = "ingested"


class InterviewListItem(BaseModel):
    id: uuid.UUID
    source_ref: str | None
    contact_name: str | None
    sentiment: str | None
    language: str
    created_at: datetime
