"""
ProductDiscoveryGraph — LangGraph StateGraph that transforms raw customer
interviews into a fully validated AgenticHandoffPayload.

Pipeline:
    scrub_pii → synthesize_insights → draft_feature_strategy
              → generate_tech_specs  → assemble_handoff → END
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.nodes import (
    assemble_handoff,
    draft_feature_strategy,
    generate_tech_specs,
    scrub_pii,
    synthesize_insights,
)
from app.agents.state import ProductDiscoveryState


def _has_errors(state: ProductDiscoveryState) -> str:
    if state.get("errors"):
        return "abort"
    return "continue"


def build_product_discovery_graph() -> StateGraph:
    g = StateGraph(ProductDiscoveryState)

    # Nodes
    g.add_node("scrub_pii", scrub_pii)
    g.add_node("synthesize_insights", synthesize_insights)
    g.add_node("draft_feature_strategy", draft_feature_strategy)
    g.add_node("generate_tech_specs", generate_tech_specs)
    g.add_node("assemble_handoff", assemble_handoff)

    # Edges — linear pipeline with error short-circuits
    g.set_entry_point("scrub_pii")

    g.add_conditional_edges("scrub_pii", _has_errors, {"abort": END, "continue": "synthesize_insights"})
    g.add_conditional_edges("synthesize_insights", _has_errors, {"abort": END, "continue": "draft_feature_strategy"})
    g.add_conditional_edges("draft_feature_strategy", _has_errors, {"abort": END, "continue": "generate_tech_specs"})
    g.add_conditional_edges("generate_tech_specs", _has_errors, {"abort": END, "continue": "assemble_handoff"})
    g.add_edge("assemble_handoff", END)

    return g


product_discovery_graph = build_product_discovery_graph().compile()
