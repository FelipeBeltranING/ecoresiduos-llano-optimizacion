import { useLocation } from "react-router-dom";

import { findNavItem } from "@/navigation";

import { Brand } from "./Brand";

export function TopBar() {
  const { pathname } = useLocation();
  const current = findNavItem(pathname);

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="flex h-16 items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
        <div className="min-w-0 lg:hidden">
          <Brand />
        </div>

        <div className="hidden min-w-0 lg:block">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            {current?.label ?? "Panel"}
          </p>
          <p className="truncate text-sm text-slate-600">
            {current?.description ?? "Resumen de la red y del sprint"}
          </p>
        </div>

        <span className="shrink-0 rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-800">
          Sprint 1
        </span>
      </div>
    </header>
  );
}
