import { Outlet } from "react-router-dom";

import { BottomNav } from "./BottomNav";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

export function AppLayout() {
  return (
    <div className="min-h-dvh bg-slate-50">
      <a
        href="#contenido"
        className="sr-only z-50 rounded-lg bg-brand-700 px-4 py-2 text-sm font-medium text-white focus:not-sr-only focus:fixed focus:left-4 focus:top-4"
      >
        Saltar al contenido
      </a>

      <Sidebar />

      <div className="lg:pl-64">
        <TopBar />
        <main
          id="contenido"
          className="mx-auto w-full max-w-7xl px-4 pb-24 pt-6 sm:px-6 lg:px-8 lg:pb-12"
        >
          <Outlet />
        </main>
      </div>

      <BottomNav />
    </div>
  );
}
