"use client";

import { motion } from "framer-motion";
import { FileText, Layers, Ticket } from "lucide-react";
import { GlowingCard } from "@/components/ui/glowing-card";
import { PriorityBadge, StatusBadge } from "@/components/ui/priority-badge";
import { useDashboardStore } from "@/store/use-dashboard-store";
import type { PrdListItem } from "@/actions/dashboard";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0 },
};

export function PrdGrid({ prds }: { prds: PrdListItem[] }) {
  const openPrdDrawer = useDashboardStore((s) => s.openPrdDrawer);

  if (prds.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border/50 py-16 text-center">
        <FileText className="h-10 w-10 text-muted-foreground/50" />
        <p className="mt-3 text-sm text-muted-foreground">
          No Feature PRDs yet. Run a Discovery workflow to generate your first PRD.
        </p>
      </div>
    );
  }

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3"
    >
      {prds.map((prd) => (
        <motion.div key={prd.id} variants={item}>
          <GlowingCard onClick={() => openPrdDrawer(prd.id)}>
            <div className="flex items-start justify-between gap-3">
              <h3 className="font-semibold leading-snug line-clamp-2">
                {prd.title}
              </h3>
              <PriorityBadge priority={prd.priority} />
            </div>

            <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
              {prd.rationale}
            </p>

            {prd.targetPersona && (
              <p className="mt-2 text-xs text-muted-foreground/70">
                Persona: {prd.targetPersona}
              </p>
            )}

            <div className="mt-4 flex items-center justify-between">
              <StatusBadge status={prd.status} />
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Layers className="h-3.5 w-3.5" />
                  {prd.uiSpecCount}
                </span>
                <span className="flex items-center gap-1">
                  <Ticket className="h-3.5 w-3.5" />
                  {prd.ticketCount}
                </span>
              </div>
            </div>
          </GlowingCard>
        </motion.div>
      ))}
    </motion.div>
  );
}
