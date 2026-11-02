import { NavLink } from "react-router-dom";

import { navigation } from "@/navigation";

import { Brand } from "./Brand";

function linkClasses(isActive: boolean): string {
  return [
    "group flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition-colors",
    isActive
      ? "bg-brand-50 text-brand-800"
      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
  ].join(" ");
}

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-slate-200 bg-white lg:flex">
      <div className="px-4 py-5">
        <Brand />
      </div>

      <nav aria-label="Navegación principal" className="flex-1 space-y-6 overflow-y-auto px-3 pb-6">
        {navigation.map((group) => (
          <div key={group.label}>
            <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              {group.label}
            </p>
            <ul className="space-y-1">
              {group.items.map((item) => (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    end={item.end}
                    className={({ isActive }) => linkClasses(isActive)}
                  >
                    {({ isActive }) => (
                      <>
                        <item.icon
                          className={
                            isActive
                              ? "size-4 shrink-0 text-brand-700"
                              : "size-4 shrink-0 text-slate-400"
                          }
                          aria-hidden="true"
                        />
                        <span className="truncate">{item.label}</span>
                      </>
                    )}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>

      <div className="border-t border-slate-200 p-4">
        <p className="text-xs font-medium text-slate-600">Sprint 1 · v0.1.0</p>
        <p className="mt-1 text-[11px] text-slate-400">Frontend base · T-01c</p>
      </div>
    </aside>
  );
}
