import {
  FlaskConical,
  Gauge,
  GitCompareArrows,
  History,
  LayoutDashboard,
  Network,
  Route as RouteIcon,
  Sprout,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  to: string;
  label: string;
  shortLabel: string;
  description: string;
  icon: LucideIcon;
  end?: boolean;
  primary?: boolean;
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

export const navigation: NavGroup[] = [
  {
    label: "Operación",
    items: [
      {
        to: "/",
        label: "Panel",
        shortLabel: "Panel",
        description: "Resumen de la red y del sprint",
        icon: LayoutDashboard,
        end: true,
        primary: true,
      },
      {
        to: "/red",
        label: "Red logística",
        shortLabel: "Red",
        description: "Empresas, plantas y centros de acopio",
        icon: Network,
        primary: true,
      },
      {
        to: "/rutas",
        label: "Rutas y costos",
        shortLabel: "Rutas",
        description: "Distancias y matriz de costos",
        icon: RouteIcon,
        primary: true,
      },
    ],
  },
  {
    label: "Optimización",
    items: [
      {
        to: "/exacto",
        label: "Modelo exacto",
        shortLabel: "Exacto",
        description: "Solución óptima con PuLP y CBC",
        icon: Gauge,
        primary: true,
      },
      {
        to: "/ag",
        label: "Algoritmo genético",
        shortLabel: "AG",
        description: "Configuración, ejecución y convergencia",
        icon: Sprout,
      },
      {
        to: "/sensibilidad",
        label: "Sensibilidad",
        shortLabel: "Sensib.",
        description: "Escenarios, precios sombra y rangos",
        icon: FlaskConical,
      },
    ],
  },
  {
    label: "Análisis",
    items: [
      {
        to: "/comparativo",
        label: "Comparativo",
        shortLabel: "Comparar",
        description: "Exacto frente a AG, brecha y escalabilidad",
        icon: GitCompareArrows,
      },
      {
        to: "/historial",
        label: "Historial",
        shortLabel: "Historial",
        description: "Ejecuciones, escenarios y reportes",
        icon: History,
      },
    ],
  },
];

export const allNavItems: NavItem[] = navigation.flatMap((group) => group.items);

export const primaryNavItems: NavItem[] = allNavItems.filter((item) => item.primary);

export const secondaryNavItems: NavItem[] = allNavItems.filter((item) => !item.primary);

/** Finds the deepest navigation entry that matches the current path. */
export function findNavItem(pathname: string): NavItem | undefined {
  return [...allNavItems]
    .sort((a, b) => b.to.length - a.to.length)
    .find((item) => (item.end ? pathname === item.to : pathname.startsWith(item.to)));
}
