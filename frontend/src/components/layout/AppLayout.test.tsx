import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { routes } from "@/router";

// Leaflet necesita un navegador real; en jsdom se reemplaza el mapa por un marcador
vi.mock("@/components/mapa/MapaReal", () => ({
  MapaReal: () => <div data-testid="mapa-real" />,
}));

function renderApp(initialPath = "/") {
  const router = createMemoryRouter(routes, { initialEntries: [initialPath] });
  const cliente = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={cliente}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}

describe("app shell", () => {
  it("renders the control panel with both navigation landmarks", () => {
    renderApp();

    expect(screen.getByRole("heading", { level: 1, name: "Panel de control" })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Navegación principal" })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Navegación rápida" })).toBeInTheDocument();
  });

  it("navigates to another module from the topbar", async () => {
    const user = userEvent.setup();
    renderApp();

    await user.click(screen.getByRole("link", { name: "Rutas" }));

    expect(screen.getByRole("heading", { level: 1, name: "Rutas y costos" })).toBeInTheDocument();
  });

  it("opens the additional modules sheet from the mobile navigation", async () => {
    const user = userEvent.setup();
    renderApp();

    await user.click(screen.getByRole("button", { name: "Más" }));

    const dialog = screen.getByRole("dialog", { name: "Más módulos" });
    expect(within(dialog).getByRole("link", { name: /Genético/ })).toBeInTheDocument();
  });

  it("renders the not-found view for unknown routes", () => {
    renderApp("/ruta-inexistente");

    expect(
      screen.getByRole("heading", { level: 1, name: "Página no encontrada" }),
    ).toBeInTheDocument();
  });
});
