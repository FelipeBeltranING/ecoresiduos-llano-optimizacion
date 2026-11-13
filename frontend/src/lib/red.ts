import type { Flujo, Nodo, Sensibilidad } from "@/api/tipos";
import type { UsoPlanta } from "@/components/mapa/MapaReal";

export const CODIGO_FICTICIA = "FICTICIA";

/** Toneladas recibidas por cada planta frente a su capacidad. */
export function usoDePlantas(nodos: Nodo[], flujos: Flujo[]): Record<string, UsoPlanta> {
  const uso: Record<string, UsoPlanta> = {};
  for (const nodo of nodos) {
    if (nodo.tipo === "PLANTA" && nodo.activo) {
      uso[nodo.codigo] = { uso: 0, capacidad: nodo.capacidad_t ?? 0 };
    }
  }
  for (const flujo of flujos) {
    if (uso[flujo.destino]) uso[flujo.destino].uso += flujo.toneladas;
  }
  return uso;
}

export function valorSensibilidad(
  registros: Sensibilidad[],
  tipo: Sensibilidad["tipo"],
  elemento: string,
): Sensibilidad | undefined {
  return registros.find((r) => r.tipo === tipo && r.elemento === elemento);
}

export const activos = (nodos: Nodo[] | undefined) => (nodos ?? []).filter((n) => n.activo);

export function descargar(url: string) {
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.rel = "noopener";
  enlace.target = "_blank";
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();
}

export function formatoFecha(iso: string): string {
  return new Intl.DateTimeFormat("es-CO", { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(iso),
  );
}

/** Toneladas que entran a cada centro de acopio activo frente a su capacidad (HU-17). */
export function usoDeAcopios(nodos: Nodo[], flujos: Flujo[]): Record<string, UsoPlanta> {
  const uso: Record<string, UsoPlanta> = {};
  for (const nodo of nodos) {
    if (nodo.tipo === "ACOPIO" && nodo.activo) {
      uso[nodo.codigo] = { uso: 0, capacidad: nodo.capacidad_t ?? 0 };
    }
  }
  for (const flujo of flujos) {
    if (uso[flujo.destino]) uso[flujo.destino].uso += flujo.toneladas;
  }
  return uso;
}

/** La ejecución corresponde a la red activa si envía flujo desde exactamente las mismas empresas. */
export function ejecucionVigente(flujos: Flujo[], nodos: Nodo[]): boolean {
  const empresas = new Set(
    nodos
      .filter((n) => n.activo && n.tipo === "FUENTE" && (n.oferta_t ?? 0) > 0)
      .map((n) => n.codigo),
  );
  
  const acopios = new Set(nodos.filter((n) => n.tipo === "ACOPIO").map((n) => n.codigo));
  const origenes = new Set(flujos.map((f) => f.origen).filter((codigo) => !acopios.has(codigo)));
  if (empresas.size !== origenes.size) return false;
  return [...origenes].every((codigo) => empresas.has(codigo));
}
