"use server";

import { prisma } from "@/lib/db";
import { requireAuth } from "@/lib/auth";
import type { PrdStatus, AgentRunStatus, Priority } from "@prisma/client";

// ─── Types ──────────────────────────────────────────────────────────────────

export interface DashboardCounts {
  totalPrds: number;
  approvedPrds: number;
  totalInterviews: number;
  activeAgentRuns: number;
}

export interface PrdListItem {
  id: string;
  title: string;
  rationale: string;
  status: PrdStatus;
  priority: Priority;
  targetPersona: string | null;
  ticketCount: number;
  uiSpecCount: number;
  createdAt: Date;
}

export interface AgentRunItem {
  id: string;
  status: AgentRunStatus;
  graphName: string;
  tokenUsage: number;
  errorMessage: string | null;
  startedAt: Date | null;
  completedAt: Date | null;
  createdAt: Date;
}

// ─── Server Actions ─────────────────────────────────────────────────────────

export async function getDashboardCounts(): Promise<DashboardCounts> {
  const session = await requireAuth();
  const orgFilter = { organization_id: session.organizationId, deleted_at: null };

  const [totalPrds, approvedPrds, totalInterviews, activeAgentRuns] =
    await Promise.all([
      prisma.featurePrd.count({ where: orgFilter }),
      prisma.featurePrd.count({ where: { ...orgFilter, status: "APPROVED" } }),
      prisma.interview.count({ where: orgFilter }),
      prisma.agentRun.count({
        where: {
          organization_id: session.organizationId,
          status: { in: ["QUEUED", "RUNNING"] },
        },
      }),
    ]);

  return { totalPrds, approvedPrds, totalInterviews, activeAgentRuns };
}

export async function getFeaturePrds(
  status?: PrdStatus,
): Promise<PrdListItem[]> {
  const session = await requireAuth();

  const prds = await prisma.featurePrd.findMany({
    where: {
      organization_id: session.organizationId,
      deleted_at: null,
      ...(status ? { status } : {}),
    },
    orderBy: [
      { priority: "asc" },
      { created_at: "desc" },
    ],
    include: {
      _count: { select: { jira_tickets: true, ui_specs: true } },
    },
    take: 50,
  });

  return prds.map((p) => ({
    id: p.id,
    title: p.title,
    rationale: p.rationale,
    status: p.status,
    priority: p.priority,
    targetPersona: p.target_persona,
    ticketCount: p._count.jira_tickets,
    uiSpecCount: p._count.ui_specs,
    createdAt: p.created_at,
  }));
}

export async function getRecentAgentRuns(): Promise<AgentRunItem[]> {
  const session = await requireAuth();

  const runs = await prisma.agentRun.findMany({
    where: { organization_id: session.organizationId },
    orderBy: { created_at: "desc" },
    take: 10,
  });

  return runs.map((r) => ({
    id: r.id,
    status: r.status,
    graphName: r.graph_name,
    tokenUsage: r.token_usage,
    errorMessage: r.error_message,
    startedAt: r.started_at,
    completedAt: r.completed_at,
    createdAt: r.created_at,
  }));
}
