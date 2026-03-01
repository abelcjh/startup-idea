"""
Agentic Handoff Schema — strict Pydantic v2 models enforcing the structured
output contract between LangGraph agents (via Mistral) and the ProductOS API.

LLM function-calling / structured-output must conform exactly to these types.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


# ─── Enums ───────────────────────────────────────────────────────────────────


class Priority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TicketType(StrEnum):
    EPIC = "epic"
    STORY = "story"
    TASK = "task"
    BUG = "bug"


class Sentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


# ─── Interview Synthesis ─────────────────────────────────────────────────────


class InterviewSignal(BaseModel):
    """Single extracted signal from a customer interview."""

    model_config = {"strict": True}

    quote: str = Field(..., description="Verbatim customer quote (PII-scrubbed)")
    pain_point: str = Field(..., description="Distilled pain point")
    sentiment: Sentiment = Field(..., description="Detected sentiment")
    frequency: int = Field(
        default=1, ge=1, description="Number of interviews containing this signal"
    )


class InsightClusterOutput(BaseModel):
    """Grouped insight synthesized from multiple interview signals."""

    model_config = {"strict": True}

    title: str = Field(..., max_length=200, description="Short cluster label")
    description: str = Field(..., description="Synthesized narrative of the insight")
    signals: list[InterviewSignal] = Field(
        ..., min_length=1, description="Supporting interview signals"
    )
    total_signal_count: int = Field(..., ge=1, description="Total corroborating signals")


# ─── UI Spec ─────────────────────────────────────────────────────────────────


class UiComponentSpec(BaseModel):
    """Specification for a single UI component the PRD requires."""

    model_config = {"strict": True}

    component_name: str = Field(
        ..., description="PascalCase React component name, e.g. 'InsightDashboard'"
    )
    description: str = Field(..., description="What this component does and why")
    props: dict[str, str] = Field(
        default_factory=dict,
        description="Prop name → TypeScript type string, e.g. {'items': 'InsightItem[]'}",
    )
    layout_hint: str | None = Field(
        default=None, description="Placement hint: 'sidebar', 'modal', 'full-page', etc."
    )
    sort_order: int = Field(default=0, ge=0, description="Render order in the feature view")


# ─── Jira Tickets ────────────────────────────────────────────────────────────


class JiraTicketSpec(BaseModel):
    """Technical handoff ticket to be synced to Jira."""

    model_config = {"strict": True}

    type: TicketType = Field(default=TicketType.STORY, description="Jira issue type")
    title: str = Field(..., max_length=255, description="Ticket summary line")
    description: str = Field(..., description="Technical implementation details (Markdown)")
    acceptance_criteria: list[str] = Field(
        ..., min_length=1, description="Definition-of-done checklist items"
    )
    story_points: int | None = Field(
        default=None, ge=1, le=21, description="Fibonacci estimate"
    )


# ─── Success Metrics ─────────────────────────────────────────────────────────


class SuccessMetric(BaseModel):
    """KPI attached to a feature PRD."""

    model_config = {"strict": True}

    metric_name: str = Field(..., description="e.g. 'NPS delta', 'task completion rate'")
    target_value: str = Field(..., description="Target with unit, e.g. '+10 NPS', '>85%'")
    measurement_method: str = Field(..., description="How this metric is measured")


# ─── Feature PRD (top-level handoff) ─────────────────────────────────────────


class FeaturePrdHandoff(BaseModel):
    """
    Complete agentic handoff payload produced by the LangGraph PRD-generation
    graph. This is the single structured output written to `AgentRun.output_payload`
    and consumed by the Next.js frontend + Jira sync worker.
    """

    model_config = {"strict": True}

    feature_name: str = Field(..., max_length=200, description="Feature title")
    rationale: str = Field(..., description="Business justification grounded in user evidence")
    priority: Priority = Field(default=Priority.MEDIUM, description="Triage priority")
    target_persona: str | None = Field(
        default=None, description="Primary user persona this feature serves"
    )
    insight_cluster: InsightClusterOutput = Field(
        ..., description="Synthesized insight cluster backing this feature"
    )
    success_metrics: list[SuccessMetric] = Field(
        ..., min_length=1, description="Measurable KPIs"
    )
    ui_components: list[UiComponentSpec] = Field(
        ..., min_length=1, description="UI component specifications"
    )
    jira_tickets: list[JiraTicketSpec] = Field(
        ..., min_length=1, description="Technical handoff tickets"
    )


# ─── Batch wrapper (multi-feature agent runs) ────────────────────────────────


class AgenticHandoffPayload(BaseModel):
    """Top-level wrapper when the agent produces multiple PRDs in one run."""

    model_config = {"strict": True}

    run_id: str = Field(..., description="AgentRun UUID for traceability")
    organization_id: str = Field(..., description="Tenant UUID")
    features: list[FeaturePrdHandoff] = Field(
        ..., min_length=1, description="Generated feature PRDs"
    )
    total_token_usage: int = Field(default=0, ge=0, description="Aggregate LLM tokens consumed")
