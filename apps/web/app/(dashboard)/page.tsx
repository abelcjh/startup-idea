import { FileText, MessageSquareText, Bot, CheckCircle2 } from "lucide-react";
import { getDashboardCounts, getFeaturePrds, getRecentAgentRuns } from "@/actions/dashboard";
import { StatCard } from "@/components/ui/stat-card";
import { PrdGrid } from "@/components/dashboard/prd-grid";
import { AgentRunsFeed } from "@/components/dashboard/agent-runs-feed";

export default async function DashboardPage() {
  const [counts, prds, agentRuns] = await Promise.all([
    getDashboardCounts(),
    getFeaturePrds(),
    getRecentAgentRuns(),
  ]);

  return (
    <>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          AI-powered product discovery overview
        </p>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total PRDs"
          value={counts.totalPrds}
          icon={<FileText className="h-5 w-5" />}
          accentClass="bg-blue-500"
        />
        <StatCard
          label="Approved"
          value={counts.approvedPrds}
          icon={<CheckCircle2 className="h-5 w-5" />}
          accentClass="bg-emerald-500"
        />
        <StatCard
          label="Interviews"
          value={counts.totalInterviews}
          icon={<MessageSquareText className="h-5 w-5" />}
          accentClass="bg-purple-500"
        />
        <StatCard
          label="Active Runs"
          value={counts.activeAgentRuns}
          icon={<Bot className="h-5 w-5" />}
          accentClass="bg-orange-500"
        />
      </div>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Feature PRDs</h2>
            <span className="text-sm text-muted-foreground">
              {prds.length} total
            </span>
          </div>
          <PrdGrid prds={prds} />
        </div>

        <div>
          <h2 className="mb-4 text-lg font-semibold">Recent Agent Runs</h2>
          <AgentRunsFeed runs={agentRuns} />
        </div>
      </div>
    </>
  );
}
