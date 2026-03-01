import { create } from "zustand";
import type { PrdStatus } from "@prisma/client";

interface DashboardState {
  selectedPrdId: string | null;
  isPrdDrawerOpen: boolean;
  statusFilter: PrdStatus | null;

  setSelectedPrd: (id: string | null) => void;
  openPrdDrawer: (id: string) => void;
  closePrdDrawer: () => void;
  setStatusFilter: (status: PrdStatus | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  selectedPrdId: null,
  isPrdDrawerOpen: false,
  statusFilter: null,

  setSelectedPrd: (id) => set({ selectedPrdId: id }),
  openPrdDrawer: (id) => set({ selectedPrdId: id, isPrdDrawerOpen: true }),
  closePrdDrawer: () => set({ isPrdDrawerOpen: false }),
  setStatusFilter: (status) => set({ statusFilter: status }),
}));
