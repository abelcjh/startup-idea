import { cn } from "@/lib/utils";
import type { Priority, PrdStatus } from "@prisma/client";

const PRIORITY_STYLES: Record<Priority, string> = {
  CRITICAL: "bg-red-500/15 text-red-400 border-red-500/30",
  HIGH: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  MEDIUM: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  LOW: "bg-neutral-500/15 text-neutral-400 border-neutral-500/30",
};

const STATUS_STYLES: Record<PrdStatus, string> = {
  DRAFT: "bg-neutral-500/15 text-neutral-400 border-neutral-500/30",
  IN_REVIEW: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  APPROVED: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  ARCHIVED: "bg-neutral-500/15 text-neutral-500 border-neutral-500/30",
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium", PRIORITY_STYLES[priority])}>
      {priority}
    </span>
  );
}

export function StatusBadge({ status }: { status: PrdStatus }) {
  const label = status.replace("_", " ");
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium", STATUS_STYLES[status])}>
      {label}
    </span>
  );
}
