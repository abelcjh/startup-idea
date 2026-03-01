"""SQLModel table mirroring the Prisma `agent_runs` schema."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlmodel import Column, DateTime, Enum, Field, SQLModel, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID


class AgentRunStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentRun(SQLModel, table=True):
    __tablename__ = "agent_runs"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    )
    organization_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), nullable=False, index=True))
    triggered_by_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), nullable=False))
    status: AgentRunStatus = Field(
        default=AgentRunStatus.QUEUED,
        sa_column=Column(Enum(AgentRunStatus, name="agentrunstatus"), nullable=False, index=True),
    )
    graph_name: str
    input_payload: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False, server_default="{}"))
    output_payload: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    token_usage: int = Field(default=0)
    error_message: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )
