import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

import { primaryNavItems, secondaryNavItems } from "@/navigation";

function itemClasses(isActive: boolean): string {
  return [
    "flex items-center gap-2 rounded-xl px-3 py-3 text-sm font-medium transition-colors",
    isActive ? "bg-brand-50 text-brand-800" : "bg-slate-50 text-slate-700 hover:bg-slate-100",
  ].join(" ");
}

export function BottomNav() {
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const { pathname } = useLocation();

  useEffect(() => {
    setIsSheetOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!isSheetOpen) return;

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setIsSheetOpen(false);
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isSheetOpen]);

  return (
    <>
      {isSheetOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Cerrar menú"
            className="absolute inset-0 bg-slate-900/40 backdrop-blur-[2px]"
            onClick={() => setIsSheetOpen(false)}
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Más módulos"
            className="absolute inset-x-0 bottom-0 rounded-t-3xl border-t border-slate-200 bg-white p-4 pb-[calc(1rem+env(safe-area-inset-bottom))] shadow-2xl"
          >
            <div className="mx-auto mb-3 h-1 w-10 rounded-full bg-slate-300" />
            <div className="mb-2 flex items-center justify-between px-1">
              <p className="text-sm font-semibold text-slate-900">Más módulos</p>
              <button
                type="button"
                onClick={() => setIsSheetOpen(false)}
                aria-label="Cerrar menú"
                className="rounded-lg p-1 text-slate-500 hover:bg-slate-100"
              >
                <X className="size-5" aria-hidden="true" />
              </button>
            </div>
            <ul className="grid grid-cols-2 gap-2">
              {secondaryNavItems.map((item) => (
                <li key={item.to}>
                  <NavLink to={item.to} className={({ isActive }) => itemClasses(isActive)}>
                    <item.icon className="size-5 shrink-0" aria-hidden="true" />
                    <span>{item.label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}

      <nav
        aria-label="Navegación rápida"
        className="fixed inset-x-0 bottom-0 z-30 border-t border-slate-200 bg-white/95 pb-[env(safe-area-inset-bottom)] backdrop-blur lg:hidden"
      >
        <ul className="mx-auto grid max-w-md grid-cols-5">
          {primaryNavItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  [
                    "flex flex-col items-center gap-0.5 px-1 py-2 text-[11px] font-medium transition-colors",
                    isActive ? "text-brand-700" : "text-slate-500 hover:text-slate-800",
                  ].join(" ")
                }
              >
                <item.icon className="size-5" aria-hidden="true" />
                <span>{item.shortLabel}</span>
              </NavLink>
            </li>
          ))}
          <li>
            <button
              type="button"
              onClick={() => setIsSheetOpen(true)}
              aria-expanded={isSheetOpen}
              aria-haspopup="dialog"
              className="flex w-full flex-col items-center gap-0.5 px-1 py-2 text-[11px] font-medium text-slate-500 transition-colors hover:text-slate-800"
            >
              <Menu className="size-5" aria-hidden="true" />
              <span>Más</span>
            </button>
          </li>
        </ul>
      </nav>
    </>
  );
}
