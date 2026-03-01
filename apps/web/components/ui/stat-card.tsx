"use client";

import { type ReactNode } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: number;
  icon: ReactNode;
  accentClass?: string;
}

export function StatCard({ label, value, icon, accentClass }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn(
        "relative overflow-hidden rounded-xl border border-border/50 bg-card p-5",
      )}
    >
      <div className={cn("absolute -right-3 -top-3 h-16 w-16 rounded-full opacity-10 blur-2xl", accentClass ?? "bg-primary")} />
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted text-muted-foreground">
          {icon}
        </div>
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-2xl font-bold tracking-tight">{value}</p>
        </div>
      </div>
    </motion.div>
  );
}
