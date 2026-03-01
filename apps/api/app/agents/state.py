"""ProductDiscoveryGraph state definition and intermediate LLM output models."""

from __future__ import annotations

from typing import TypedDict

from pydantic import BaseModel, Field

from app.schemas.handoff import (
    AgenticHandoffPayload,
    InsightClusterOutput,
    JiraTicketSpec,
    Priority,
    SuccessMetric,
    UiComponentSpec,
)


# ─── Intermediate LLM-bound models (not part of public handoff contract) ─────


class FeatureStrategyOutput(BaseModel):
    """LLM output for the business-strategy node (no tech specs yet)."""

    model_config = {"strict": True}

    feature_name: str = Field(..., max_length=200, description="Feature title")
    rationale: str = Field(..., description="Business justification grounded in evidence")
    priority: Priority = Field(default=Priority.MEDIUM)
    target_persona: str | None = Field(default=None, description="Primary user persona")
    success_metrics: list[SuccessMetric] = Field(..., min_length=1)


class TechSpecOutput(BaseModel):
    """LLM output for the technical-specification node."""

    model_config = {"strict": True}

    ui_components: list[UiComponentSpec] = Field(..., min_length=1)
    jira_tickets: list[JiraTicketSpec] = Field(..., min_length=1)


# ─── Graph State ─────────────────────────────────────────────────────────────


class ProductDiscoveryState(TypedDict, total=False):
    # ── Inputs (set by caller) ──
    organization_id: str
    run_id: str
    raw_interviews: list[str]

    # ── PII-scrubbed interviews ──
    scrubbed_interviews: list[str]

    # ── Node outputs ──
    insight_cluster: InsightClusterOutput
    feature_strategy: FeatureStrategyOutput
    tech_spec: TechSpecOutput

    # ── Final assembled payload ──
    handoff_payload: AgenticHandoffPayload

    # ── Observability ──
    token_usage: int
    errors: list[str]
