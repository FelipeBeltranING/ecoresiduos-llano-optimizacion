import {
  Building2,
  ChartNoAxesColumn,
  FlaskConical,
  History,
  LayoutGrid,
  Route as RouteIcon,
  Sprout,
  Target,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  to: string;
  label: string;
  shortLabel: string;
  description: string;
  icon: LucideIcon;
  end?: boolean;
}

/** Estaciones del topbar de escritorio, en el orden del diseño Orion. */
export const allNavItems: NavItem[] = [
  {
    to: "/",
    label: "Panel",
    shortLabel: "Panel",
    description: "Resumen de la red y del sprint",
    icon: LayoutGrid,
    end: true,
  },
  {
    to: "/red",
    label: "Red",
    shortLabel: "Red",
    description: "Empresas, plantas y centros de acopio",
    icon: Building2,
  },
  {
    to: "/rutas",
    label: "Rutas",
    shortLabel: "Rutas",
    description: "Distancias y matriz de costos",
    icon: RouteIcon,
  },
  {
    to: "/exacto",
    label: "Exacto",
    shortLabel: "Exacto",
    description: "Solución óptima con PuLP y CBC",
    icon: Target,
  },
  {
    to: "/ag",
    label: "Genético",
    shortLabel: "Genético",
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
  {
    to: "/comparativo",
    label: "Comparativo",
    shortLabel: "Comparar",
    description: "Exacto frente a AG, brecha y escalabilidad",
    icon: ChartNoAxesColumn,
  },
  {
    to: "/historial",
    label: "Historial",
    shortLabel: "Historial",
    description: "Ejecuciones, escenarios y reportes",
    icon: History,
  },
];

/** Las cinco estaciones de la barra inferior móvil (la última abre el resto). */
export const mobilePrimaryPaths = ["/", "/red", "/exacto", "/comparativo"] as const;

export const mobilePrimaryNavItems: NavItem[] = mobilePrimaryPaths
  .map((path) => allNavItems.find((item) => item.to === path))
  .filter((item): item is NavItem => Boolean(item));

export const mobileMoreNavItems: NavItem[] = allNavItems.filter(
  (item) => !(mobilePrimaryPaths as readonly string[]).includes(item.to),
);

/** Finds the deepest navigation entry that matches the current path. */
export function findNavItem(pathname: string): NavItem | undefined {
  return [...allNavItems]
    .sort((a, b) => b.to.length - a.to.length)
    .find((item) => (item.end ? pathname === item.to : pathname.startsWith(item.to)));
}
