import { Outlet } from "react-router-dom";

import { BottomNav } from "./BottomNav";
import { TopBar } from "./TopBar";

export function AppLayout() {
  return (
    <div className="min-h-dvh bg-bg">
      <a
        href="#contenido"
        className="sr-only z-50 rounded-control bg-primary px-4 py-2 text-sm font-semibold text-white focus:not-sr-only focus:fixed focus:left-4 focus:top-4"
      >
        Saltar al contenido
      </a>

      <TopBar />

      <main id="contenido" className="pb-24 xl:pb-0">
        <Outlet />
      </main>

      <BottomNav />
    </div>
  );
}
