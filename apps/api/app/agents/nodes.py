"""
ProductDiscoveryGraph node functions.

Pipeline: scrub_pii → synthesize_insights → draft_feature_strategy
          → generate_tech_specs → assemble_handoff
"""

from __future__ import annotations

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm
from app.agents.state import (
    FeatureStrategyOutput,
    ProductDiscoveryState,
    TechSpecOutput,
)
from app.schemas.handoff import (
    AgenticHandoffPayload,
    FeaturePrdHandoff,
    InsightClusterOutput,
)
from app.services import pii

logger = structlog.get_logger(__name__)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _extract_tokens(raw_msg: object) -> int:
    meta = getattr(raw_msg, "usage_metadata", None)
    if meta and isinstance(meta, dict):
        return int(meta.get("total_tokens", 0))
    return 0


# ─── Node: PII Scrubbing ────────────────────────────────────────────────────


async def scrub_pii(state: ProductDiscoveryState) -> dict:
    org_id = state.get("organization_id", "")
    logger.info("node.scrub_pii.start", tenant_id=org_id, count=len(state["raw_interviews"]))

    scrubbed = pii.scrub_batch(state["raw_interviews"], tenant_id=org_id)

    logger.info("node.scrub_pii.done", tenant_id=org_id, scrubbed_count=len(scrubbed))
    return {"scrubbed_interviews": scrubbed, "token_usage": 0, "errors": []}


# ─── Node: Synthesize Insights ───────────────────────────────────────────────


_INSIGHT_SYSTEM = """\
You are a senior product researcher. Analyze the customer interview transcripts below.
Extract recurring pain points, group them into a single coherent insight cluster,
and cite verbatim quotes (already PII-scrubbed). Be precise and evidence-driven."""


async def synthesize_insights(state: ProductDiscoveryState) -> dict:
    org_id = state.get("organization_id", "")
    logger.info("node.synthesize_insights.start", tenant_id=org_id)

    interviews_block = "\n---\n".join(state["scrubbed_interviews"])
    llm = get_llm().with_structured_output(InsightClusterOutput, include_raw=True)

    result = await llm.ainvoke([
        SystemMessage(content=_INSIGHT_SYSTEM),
        HumanMessage(content=f"Interview transcripts:\n\n{interviews_block}"),
    ])

    tokens = _extract_tokens(result["raw"])
    parsed: InsightClusterOutput = result["parsed"]

    logger.info(
        "node.synthesize_insights.done",
        tenant_id=org_id,
        cluster_title=parsed.title,
        signal_count=parsed.total_signal_count,
        tokens=tokens,
    )
    return {
        "insight_cluster": parsed,
        "token_usage": state.get("token_usage", 0) + tokens,
    }


# ─── Node: Draft Feature Strategy ───────────────────────────────────────────


_STRATEGY_SYSTEM = """\
You are a senior product strategist. Given the synthesized insight cluster,
draft a feature proposal with a clear business rationale, triage priority,
target persona, and measurable success metrics (KPIs).
Ground every claim in the evidence from the insight cluster."""


async def draft_feature_strategy(state: ProductDiscoveryState) -> dict:
    org_id = state.get("organization_id", "")
    logger.info("node.draft_feature_strategy.start", tenant_id=org_id)

    cluster_json = state["insight_cluster"].model_dump_json(indent=2)
    llm = get_llm().with_structured_output(FeatureStrategyOutput, include_raw=True)

    result = await llm.ainvoke([
        SystemMessage(content=_STRATEGY_SYSTEM),
        HumanMessage(content=f"Insight cluster:\n\n{cluster_json}"),
    ])

    tokens = _extract_tokens(result["raw"])
    parsed: FeatureStrategyOutput = result["parsed"]

    logger.info(
        "node.draft_feature_strategy.done",
        tenant_id=org_id,
        feature=parsed.feature_name,
        priority=parsed.priority.value,
        tokens=tokens,
    )
    return {
        "feature_strategy": parsed,
        "token_usage": state.get("token_usage", 0) + tokens,
    }


# ─── Node: Generate Technical Specs ─────────────────────────────────────────


_TECH_SPEC_SYSTEM = """\
You are a senior frontend architect and engineering lead. Given a feature PRD
and its backing insight cluster, produce:
1. UI component specifications (PascalCase React components, props as TS types,
   layout hints). Prioritize mobile-first, low-bandwidth rendering.
2. Jira tickets (epics/stories/tasks) with acceptance criteria and story-point
   estimates (Fibonacci). Cover frontend, backend, and testing work."""


async def generate_tech_specs(state: ProductDiscoveryState) -> dict:
    org_id = state.get("organization_id", "")
    logger.info("node.generate_tech_specs.start", tenant_id=org_id)

    context = (
        f"Feature: {state['feature_strategy'].model_dump_json(indent=2)}\n\n"
        f"Insight cluster: {state['insight_cluster'].model_dump_json(indent=2)}"
    )
    llm = get_llm().with_structured_output(TechSpecOutput, include_raw=True)

    result = await llm.ainvoke([
        SystemMessage(content=_TECH_SPEC_SYSTEM),
        HumanMessage(content=context),
    ])

    tokens = _extract_tokens(result["raw"])
    parsed: TechSpecOutput = result["parsed"]

    logger.info(
        "node.generate_tech_specs.done",
        tenant_id=org_id,
        ui_components=len(parsed.ui_components),
        jira_tickets=len(parsed.jira_tickets),
        tokens=tokens,
    )
    return {
        "tech_spec": parsed,
        "token_usage": state.get("token_usage", 0) + tokens,
    }


# ─── Node: Assemble Final Handoff ───────────────────────────────────────────


async def assemble_handoff(state: ProductDiscoveryState) -> dict:
    org_id = state.get("organization_id", "")
    logger.info("node.assemble_handoff.start", tenant_id=org_id)

    strategy = state["feature_strategy"]
    cluster = state["insight_cluster"]
    tech = state["tech_spec"]

    feature = FeaturePrdHandoff(
        feature_name=strategy.feature_name,
        rationale=strategy.rationale,
        priority=strategy.priority,
        target_persona=strategy.target_persona,
        insight_cluster=cluster,
        success_metrics=strategy.success_metrics,
        ui_components=tech.ui_components,
        jira_tickets=tech.jira_tickets,
    )

    payload = AgenticHandoffPayload(
        run_id=state.get("run_id", ""),
        organization_id=org_id,
        features=[feature],
        total_token_usage=state.get("token_usage", 0),
    )

    logger.info(
        "node.assemble_handoff.done",
        tenant_id=org_id,
        run_id=payload.run_id,
        total_tokens=payload.total_token_usage,
    )
    return {"handoff_payload": payload}
