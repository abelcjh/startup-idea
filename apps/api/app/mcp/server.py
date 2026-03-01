"""
ProductOS MCP Server — Anthropic Model Context Protocol over SSE.

Exposes LangGraph-generated PRDs, UI specs, and Jira tickets to external
coding agents (Cursor, Claude Code, etc.) as queryable MCP tools.

Mount point: FastAPI app.mount("/mcp", mcp_app)
SSE endpoint: GET  /mcp/sse
Messages:     POST /mcp/messages/
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import structlog
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Resource, TextContent, Tool
from sqlalchemy import text
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route

from app.db import engine

logger = structlog.get_logger(__name__)

mcp = Server("product-os")
sse = SseServerTransport("/messages/")


# ─── Helpers ─────────────────────────────────────────────────────────────────


async def _query(sql: str, params: dict | None = None) -> list[dict]:
    async with engine.connect() as conn:
        result = await conn.execute(text(sql), params or {})
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]


def _json_serial(obj: object) -> str:
    """Handle UUID/datetime serialisation for JSON dumps."""
    import datetime
    import uuid

    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Not serializable: {type(obj)}")


def _to_json(rows: list[dict]) -> str:
    return json.dumps(rows, default=_json_serial, indent=2)


# ─── Resources ───────────────────────────────────────────────────────────────


@mcp.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="productos://schema/feature-prd",
            name="Feature PRD Schema",
            description="Column definitions for the feature_prds table",
            mimeType="application/json",
        ),
        Resource(
            uri="productos://schema/jira-tickets",
            name="Jira Tickets Schema",
            description="Column definitions for the jira_tickets table",
            mimeType="application/json",
        ),
        Resource(
            uri="productos://schema/ui-specs",
            name="UI Specs Schema",
            description="Column definitions for the ui_specs table",
            mimeType="application/json",
        ),
    ]


@mcp.read_resource()
async def read_resource(uri: str) -> str:
    schemas = {
        "productos://schema/feature-prd": {
            "table": "feature_prds",
            "columns": {
                "id": "uuid PK",
                "organization_id": "uuid (tenant FK)",
                "title": "string",
                "rationale": "text",
                "status": "DRAFT | IN_REVIEW | APPROVED | ARCHIVED",
                "priority": "CRITICAL | HIGH | MEDIUM | LOW",
                "target_persona": "string?",
                "success_metrics": "json (SuccessMetric[])",
            },
        },
        "productos://schema/jira-tickets": {
            "table": "jira_tickets",
            "columns": {
                "id": "uuid PK",
                "feature_prd_id": "uuid FK",
                "type": "EPIC | STORY | TASK | BUG",
                "title": "string",
                "description": "text (Markdown)",
                "acceptance_criteria": "json (string[])",
                "story_points": "int?",
                "external_ref": "string? (Jira key)",
            },
        },
        "productos://schema/ui-specs": {
            "table": "ui_specs",
            "columns": {
                "id": "uuid PK",
                "feature_prd_id": "uuid FK",
                "component_name": "string (PascalCase)",
                "description": "text",
                "props_schema": "json (prop→TS type)",
                "layout_hint": "string?",
                "sort_order": "int",
            },
        },
    }
    if uri in schemas:
        return json.dumps(schemas[uri], indent=2)
    raise ValueError(f"Unknown resource: {uri}")


# ─── Tools ───────────────────────────────────────────────────────────────────


@mcp.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_latest_prd",
            description=(
                "Fetch the highest-priority Feature PRD for an organization. "
                "Returns the PRD with its rationale, success metrics, and metadata. "
                "Use this to understand WHAT to build and WHY."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Tenant UUID",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["DRAFT", "IN_REVIEW", "APPROVED", "ARCHIVED"],
                        "description": "Filter by PRD status (default: APPROVED)",
                    },
                },
                "required": ["organization_id"],
            },
        ),
        Tool(
            name="list_feature_prds",
            description=(
                "List all Feature PRDs for an organization, ordered by priority. "
                "Returns id, title, status, and priority for each."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Tenant UUID",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 10)",
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
                "required": ["organization_id"],
            },
        ),
        Tool(
            name="get_jira_tickets",
            description=(
                "Fetch all Jira tickets for a specific Feature PRD. "
                "Returns ticket type, title, description, acceptance criteria, "
                "and story points. Use this to understand HOW to build the feature."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_prd_id": {
                        "type": "string",
                        "description": "FeaturePrd UUID",
                    },
                },
                "required": ["feature_prd_id"],
            },
        ),
        Tool(
            name="get_ui_specs",
            description=(
                "Fetch UI component specifications for a Feature PRD. "
                "Returns React component names, prop schemas (TypeScript types), "
                "layout hints, and render order. Use this to build the frontend."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_prd_id": {
                        "type": "string",
                        "description": "FeaturePrd UUID",
                    },
                },
                "required": ["feature_prd_id"],
            },
        ),
        Tool(
            name="get_full_feature_spec",
            description=(
                "Fetch the complete feature specification: PRD + UI specs + Jira tickets "
                "in a single call. This is the primary tool for a coding agent starting "
                "implementation of a new feature."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_prd_id": {
                        "type": "string",
                        "description": "FeaturePrd UUID",
                    },
                },
                "required": ["feature_prd_id"],
            },
        ),
    ]


@mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info("mcp.call_tool", tool=name, args=arguments)

    if name == "get_latest_prd":
        return await _tool_get_latest_prd(
            arguments["organization_id"],
            arguments.get("status", "APPROVED"),
        )
    if name == "list_feature_prds":
        return await _tool_list_feature_prds(
            arguments["organization_id"],
            arguments.get("limit", 10),
        )
    if name == "get_jira_tickets":
        return await _tool_get_jira_tickets(arguments["feature_prd_id"])
    if name == "get_ui_specs":
        return await _tool_get_ui_specs(arguments["feature_prd_id"])
    if name == "get_full_feature_spec":
        return await _tool_get_full_feature_spec(arguments["feature_prd_id"])

    raise ValueError(f"Unknown tool: {name}")


# ─── Tool Implementations ───────────────────────────────────────────────────


async def _tool_get_latest_prd(organization_id: str, status: str) -> list[TextContent]:
    priority_order = "CASE priority WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 WHEN 'LOW' THEN 3 END"
    rows = await _query(
        f"""
        SELECT id, title, rationale, status, priority, target_persona,
               success_metrics, created_at
        FROM feature_prds
        WHERE organization_id = :org_id
          AND status = :status
          AND deleted_at IS NULL
        ORDER BY {priority_order}, created_at DESC
        LIMIT 1
        """,
        {"org_id": organization_id, "status": status},
    )
    if not rows:
        return [TextContent(type="text", text="No PRDs found matching criteria.")]

    logger.info("mcp.get_latest_prd", tenant_id=organization_id, prd_id=str(rows[0]["id"]))
    return [TextContent(type="text", text=_to_json(rows))]


async def _tool_list_feature_prds(organization_id: str, limit: int) -> list[TextContent]:
    priority_order = "CASE priority WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 WHEN 'LOW' THEN 3 END"
    rows = await _query(
        f"""
        SELECT id, title, status, priority, target_persona, created_at
        FROM feature_prds
        WHERE organization_id = :org_id AND deleted_at IS NULL
        ORDER BY {priority_order}, created_at DESC
        LIMIT :lim
        """,
        {"org_id": organization_id, "lim": limit},
    )
    logger.info("mcp.list_feature_prds", tenant_id=organization_id, count=len(rows))
    return [TextContent(type="text", text=_to_json(rows))]


async def _tool_get_jira_tickets(feature_prd_id: str) -> list[TextContent]:
    rows = await _query(
        """
        SELECT id, type, title, description, acceptance_criteria,
               story_points, external_ref, created_at
        FROM jira_tickets
        WHERE feature_prd_id = :fid AND deleted_at IS NULL
        ORDER BY
            CASE type WHEN 'EPIC' THEN 0 WHEN 'STORY' THEN 1 WHEN 'TASK' THEN 2 WHEN 'BUG' THEN 3 END,
            created_at
        """,
        {"fid": feature_prd_id},
    )
    logger.info("mcp.get_jira_tickets", feature_prd_id=feature_prd_id, count=len(rows))
    return [TextContent(type="text", text=_to_json(rows))]


async def _tool_get_ui_specs(feature_prd_id: str) -> list[TextContent]:
    rows = await _query(
        """
        SELECT id, component_name, description, props_schema,
               layout_hint, sort_order
        FROM ui_specs
        WHERE feature_prd_id = :fid
        ORDER BY sort_order
        """,
        {"fid": feature_prd_id},
    )
    logger.info("mcp.get_ui_specs", feature_prd_id=feature_prd_id, count=len(rows))
    return [TextContent(type="text", text=_to_json(rows))]


async def _tool_get_full_feature_spec(feature_prd_id: str) -> list[TextContent]:
    prd_rows = await _query(
        """
        SELECT id, title, rationale, status, priority, target_persona,
               success_metrics, created_at
        FROM feature_prds
        WHERE id = :fid AND deleted_at IS NULL
        """,
        {"fid": feature_prd_id},
    )
    if not prd_rows:
        return [TextContent(type="text", text="Feature PRD not found.")]

    ui_rows = await _query(
        "SELECT component_name, description, props_schema, layout_hint, sort_order "
        "FROM ui_specs WHERE feature_prd_id = :fid ORDER BY sort_order",
        {"fid": feature_prd_id},
    )
    ticket_rows = await _query(
        "SELECT type, title, description, acceptance_criteria, story_points "
        "FROM jira_tickets WHERE feature_prd_id = :fid AND deleted_at IS NULL "
        "ORDER BY CASE type WHEN 'EPIC' THEN 0 WHEN 'STORY' THEN 1 WHEN 'TASK' THEN 2 WHEN 'BUG' THEN 3 END",
        {"fid": feature_prd_id},
    )

    spec = {
        "prd": prd_rows[0],
        "ui_components": ui_rows,
        "jira_tickets": ticket_rows,
    }

    logger.info(
        "mcp.get_full_feature_spec",
        feature_prd_id=feature_prd_id,
        ui_count=len(ui_rows),
        ticket_count=len(ticket_rows),
    )
    return [TextContent(type="text", text=json.dumps(spec, default=_json_serial, indent=2))]


# ─── SSE Transport Handlers ─────────────────────────────────────────────────


async def handle_sse(request: Request) -> None:
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())


async def handle_messages(request: Request) -> None:
    await sse.handle_post_message(request.scope, request.receive, request._send)


# ─── Starlette Sub-Application ──────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    logger.info("mcp_server.startup", tools=5, resources=3)
    yield
    logger.info("mcp_server.shutdown")


mcp_app = Starlette(
    lifespan=lifespan,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages/", endpoint=handle_messages, methods=["POST"]),
    ],
)
