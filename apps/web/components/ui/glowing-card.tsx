"use client";

import { type ReactNode, useCallback, useRef } from "react";
import { motion, useMotionTemplate, useMotionValue } from "framer-motion";
import { cn } from "@/lib/utils";

interface GlowingCardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export function GlowingCard({ children, className, onClick }: GlowingCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const rect = ref.current?.getBoundingClientRect();
      if (!rect) return;
      mouseX.set(e.clientX - rect.left);
      mouseY.set(e.clientY - rect.top);
    },
    [mouseX, mouseY],
  );

  const background = useMotionTemplate`
    radial-gradient(320px circle at ${mouseX}px ${mouseY}px,
      rgba(120, 119, 198, 0.12), transparent 80%)
  `;

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onClick={onClick}
      whileHover={{ scale: 1.015 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className={cn(
        "group relative cursor-pointer overflow-hidden rounded-xl",
        "border border-border/50 bg-card p-6",
        "transition-colors hover:border-primary/30",
        className,
      )}
    >
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{ background }}
      />
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}
