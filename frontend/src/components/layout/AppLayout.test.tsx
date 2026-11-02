import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { routes } from "@/router";

function renderApp(initialPath = "/") {
  const router = createMemoryRouter(routes, { initialEntries: [initialPath] });
  return render(<RouterProvider router={router} />);
}

describe("app shell", () => {
  it("renders the control panel with both navigation landmarks", () => {
    renderApp();

    expect(screen.getByRole("heading", { level: 1, name: "Panel de control" })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Navegación principal" })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Navegación rápida" })).toBeInTheDocument();
  });

  it("navigates to another module from the sidebar", async () => {
    const user = userEvent.setup();
    renderApp();

    await user.click(screen.getByRole("link", { name: "Rutas y costos" }));

    expect(screen.getByRole("heading", { level: 1, name: "Rutas y costos" })).toBeInTheDocument();
  });

  it("opens the additional modules sheet from the mobile navigation", async () => {
    const user = userEvent.setup();
    renderApp();

    await user.click(screen.getByRole("button", { name: "Más" }));

    const dialog = screen.getByRole("dialog", { name: "Más módulos" });
    expect(within(dialog).getByRole("link", { name: "Algoritmo genético" })).toBeInTheDocument();
  });

  it("renders the not-found view for unknown routes", () => {
    renderApp("/ruta-inexistente");

    expect(screen.getByRole("heading", { level: 1, name: "Página no encontrada" })).toBeInTheDocument();
  });
});
