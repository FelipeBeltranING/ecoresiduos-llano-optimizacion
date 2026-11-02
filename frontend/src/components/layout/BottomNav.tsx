import { Ellipsis, X } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

import { mobileMoreNavItems, mobilePrimaryNavItems } from "@/navigation";

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
        <div className="fixed inset-0 z-40 xl:hidden">
          <button
            type="button"
            aria-label="Cerrar menú"
            className="absolute inset-0 bg-primary-dark/40 backdrop-blur-[2px]"
            onClick={() => setIsSheetOpen(false)}
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Más módulos"
            className="absolute inset-x-0 bottom-0 rounded-t-2xl border-t border-border bg-surface p-4 pb-[calc(1.5rem+env(safe-area-inset-bottom))] shadow-2xl"
          >
            <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-border" />
            <div className="mb-3 flex items-center justify-between px-1">
              <p className="type-title-15 text-text">Más módulos</p>
              <button
                type="button"
                onClick={() => setIsSheetOpen(false)}
                aria-label="Cerrar menú"
                className="rounded-control p-1 text-muted hover:bg-bg"
              >
                <X className="size-5" aria-hidden="true" />
              </button>
            </div>
            <ul className="grid gap-2 sm:grid-cols-2">
              {mobileMoreNavItems.map((item) => (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    className={({ isActive }) =>
                      [
                        "flex items-center gap-3 rounded-control border px-3 py-3",
                        isActive
                          ? "border-primary-light bg-primary-soft text-primary-dark"
                          : "border-border text-text hover:bg-bg",
                      ].join(" ")
                    }
                  >
                    <item.icon className="size-5 shrink-0 text-primary" aria-hidden="true" />
                    <span className="min-w-0">
                      <span className="block text-sm font-semibold">{item.label}</span>
                      <span className="block text-xs text-muted">{item.description}</span>
                    </span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}

      <nav
        aria-label="Navegación rápida"
        className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-surface pb-[env(safe-area-inset-bottom)] xl:hidden"
      >
        <ul className="mx-auto grid max-w-lg grid-cols-5">
          {mobilePrimaryNavItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  [
                    "flex flex-col items-center gap-1 px-1 pb-2 pt-2.5 text-[11px] font-medium leading-4",
                    isActive ? "text-primary-dark" : "text-muted",
                  ].join(" ")
                }
              >
                {({ isActive }) => (
                  <>
                    <span
                      className={[
                        "grid size-9 place-items-center rounded-lg transition-colors",
                        isActive ? "bg-primary-soft text-primary" : "text-muted",
                      ].join(" ")}
                    >
                      <item.icon className="size-5" aria-hidden="true" />
                    </span>
                    {item.shortLabel}
                  </>
                )}
              </NavLink>
            </li>
          ))}
          <li>
            <button
              type="button"
              onClick={() => setIsSheetOpen(true)}
              aria-expanded={isSheetOpen}
              aria-haspopup="dialog"
              className="flex w-full flex-col items-center gap-1 px-1 pb-2 pt-2.5 text-[11px] font-medium leading-4 text-muted"
            >
              <span className="grid size-9 place-items-center rounded-lg">
                <Ellipsis className="size-5" aria-hidden="true" />
              </span>
              Más
            </button>
          </li>
        </ul>
      </nav>
    </>
  );
}
