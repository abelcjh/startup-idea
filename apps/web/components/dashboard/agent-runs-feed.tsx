"use client";

import { motion } from "framer-motion";
import { Bot, CheckCircle2, Loader2, XCircle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AgentRunItem } from "@/actions/dashboard";

const STATUS_CONFIG = {
  QUEUED: { icon: Clock, color: "text-neutral-400", pulse: false },
  RUNNING: { icon: Loader2, color: "text-blue-400", pulse: true },
  COMPLETED: { icon: CheckCircle2, color: "text-emerald-400", pulse: false },
  FAILED: { icon: XCircle, color: "text-red-400", pulse: false },
} as const;

function formatRelative(date: Date): string {
  const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export function AgentRunsFeed({ runs }: { runs: AgentRunItem[] }) {
  if (runs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border/50 py-10 text-center">
        <Bot className="h-8 w-8 text-muted-foreground/50" />
        <p className="mt-2 text-sm text-muted-foreground">No agent runs yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {runs.map((run, i) => {
        const { icon: Icon, color, pulse } = STATUS_CONFIG[run.status];
        return (
          <motion.div
            key={run.id}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
            className="flex items-center gap-3 rounded-lg border border-border/30 bg-card/50 px-4 py-3"
          >
            <Icon className={cn("h-4 w-4 shrink-0", color, pulse && "animate-spin")} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{run.graphName}</p>
              {run.errorMessage && (
                <p className="truncate text-xs text-red-400/80">{run.errorMessage}</p>
              )}
            </div>
            <div className="shrink-0 text-right">
              <p className={cn("text-xs font-medium", color)}>{run.status}</p>
              <p className="text-[11px] text-muted-foreground">
                {formatRelative(run.createdAt)}
              </p>
            </div>
            {run.tokenUsage > 0 && (
              <span className="shrink-0 rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
                {run.tokenUsage.toLocaleString()} tok
              </span>
            )}
          </motion.div>
        );
      })}
    </div>
  );
}
