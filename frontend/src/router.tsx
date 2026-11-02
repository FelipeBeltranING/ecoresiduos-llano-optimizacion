import { createBrowserRouter, type RouteObject } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { ComparativoPage } from "@/pages/ComparativoPage";
import { ExactoPage } from "@/pages/ExactoPage";
import { GeneticoPage } from "@/pages/GeneticoPage";
import { HistorialPage } from "@/pages/HistorialPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { PanelPage } from "@/pages/PanelPage";
import { RedPage } from "@/pages/RedPage";
import { RutasPage } from "@/pages/RutasPage";
import { SensibilidadPage } from "@/pages/SensibilidadPage";

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <PanelPage /> },
      { path: "red", element: <RedPage /> },
      { path: "rutas", element: <RutasPage /> },
      { path: "exacto", element: <ExactoPage /> },
      { path: "ag", element: <GeneticoPage /> },
      { path: "sensibilidad", element: <SensibilidadPage /> },
      { path: "comparativo", element: <ComparativoPage /> },
      { path: "historial", element: <HistorialPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
];

export const router = createBrowserRouter(routes);
