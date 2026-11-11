import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { API_URL, apiClient } from "./client";
import type {
  Ajuste,
  Analisis,
  AnalisisResumen,
  EjecucionCreada,
  EjecucionDetalle,
  Escenario,
  FuentesCasoReal,
  MatrizRutas,
  Metodo,
  Nodo,
  NodoCambios,
  NodoEntrada,
  PaginaEjecuciones,
  Parametro,
  ParametrosAG,
  Rangos,
  ResultadoEscenario,
  ResumenCaso,
  ResumenImportacion,
  RutaCambio,
  Tornado,
  Validacion,
} from "./tipos";

const get = async <T>(url: string, params?: object) =>
  (await apiClient.get<T>(url, { params })).data;
const post = async <T>(url: string, body?: unknown, timeout?: number) =>
  (await apiClient.post<T>(url, body, timeout ? { timeout } : undefined)).data;

/** Claves de caché: al cambiar la red se invalidan todas las consultas que dependen de ella. */
export const claves = {
  nodos: ["nodos"] as const,
  matriz: ["rutas", "matriz"] as const,
  parametros: ["parametros"] as const,
  validacion: ["red", "validacion"] as const,
  ejecuciones: ["ejecuciones"] as const,
  ejecucion: (id: string) => ["ejecucion", id] as const,
  escenarios: ["escenarios"] as const,
  analisis: ["analisis"] as const,
  tornado: (p: number) => ["tornado", p] as const,
};

function useInvalidarRed() {
  const cliente = useQueryClient();
  return () =>
    Promise.all(
      [claves.nodos, claves.matriz, claves.parametros, claves.validacion, ["tornado"]].map(
        (queryKey) => cliente.invalidateQueries({ queryKey }),
      ),
    );
}

// ---------- Red ----------

export const useNodos = () =>
  useQuery({ queryKey: claves.nodos, queryFn: () => get<Nodo[]>("/nodos") });

export const useMatriz = () =>
  useQuery({ queryKey: claves.matriz, queryFn: () => get<MatrizRutas>("/rutas/matriz") });

export const useParametros = () =>
  useQuery({ queryKey: claves.parametros, queryFn: () => get<Parametro[]>("/parametros") });

export const useValidacion = () =>
  useQuery({ queryKey: claves.validacion, queryFn: () => get<Validacion>("/red/validacion") });

export const useFuentesCasoReal = () =>
  useQuery({
    queryKey: ["caso-real", "fuentes"],
    queryFn: () => get<FuentesCasoReal>("/datos/caso-real/fuentes"),
    staleTime: Infinity,
  });

export function useCrearNodo() {
  const invalidar = useInvalidarRed();
  return useMutation({
    mutationFn: (nodo: NodoEntrada) => post<Nodo>("/nodos", nodo),
    onSuccess: invalidar,
  });
}

export function useActualizarNodo() {
  const invalidar = useInvalidarRed();
  return useMutation({
    mutationFn: ({ codigo, cambios }: { codigo: string; cambios: NodoCambios }) =>
      apiClient.patch<Nodo>(`/nodos/${codigo}`, cambios).then((r) => r.data),
    onSuccess: invalidar,
  });
}

export function useDesactivarNodo() {
  const invalidar = useInvalidarRed();
  return useMutation({
    mutationFn: (codigo: string) => apiClient.delete<Nodo>(`/nodos/${codigo}`).then((r) => r.data),
    onSuccess: invalidar,
  });
}

export function useActualizarRutas() {
  const invalidar = useInvalidarRed();
  return useMutation({
    mutationFn: (cambios: RutaCambio[]) =>
      apiClient
        .put<{ actualizadas: number; creadas: number }>("/rutas", cambios)
        .then((r) => r.data),
    onSuccess: invalidar,
  });
}

export function useActualizarParametro() {
  const invalidar = useInvalidarRed();
  return useMutation({
    mutationFn: ({ clave, valor }: { clave: string; valor: number }) =>
      apiClient.put<Parametro>(`/parametros/${clave}`, { valor }).then((r) => r.data),
    onSuccess: invalidar,
  });
}

export function useCargarCaso() {
  const invalidar = useInvalidarRed();
  return useMutation({
    mutationFn: (caso: "caso-base" | "caso-real") => post<ResumenCaso>(`/datos/${caso}`),
    onSuccess: invalidar,
  });
}

export function useImportarRed() {
  const invalidar = useInvalidarRed();
  return useMutation({
    mutationFn: (archivo: File) => {
      const datos = new FormData();
      datos.append("archivo", archivo);
      return post<ResumenImportacion>("/datos/importar", datos);
    },
    onSuccess: (resumen) => (resumen.importado ? invalidar() : undefined),
  });
}

// ---------- Ejecuciones ----------

export interface FiltrosEjecuciones {
  metodo?: Metodo;
  escenario_id?: string;
  solo_base?: boolean;
  desde?: string;
  hasta?: string;
  pagina?: number;
  tamano?: number;
}

export const useEjecuciones = (filtros: FiltrosEjecuciones) =>
  useQuery({
    queryKey: [...claves.ejecuciones, filtros],
    queryFn: () => get<PaginaEjecuciones>("/ejecuciones", filtros),
  });

/** Última ejecución de un método sobre la red base (sin escenario). */
export function useUltimaEjecucion(metodo: Metodo) {
  const lista = useEjecuciones({ metodo, solo_base: true, tamano: 1 });
  const id = lista.data?.items[0]?.id;
  const detalle = useEjecucion(id);
  return { id, detalle, cargando: lista.isLoading || (Boolean(id) && detalle.isLoading) };
}

export const useEjecucion = (id: string | undefined) =>
  useQuery({
    queryKey: claves.ejecucion(id ?? ""),
    queryFn: () => get<EjecucionDetalle>(`/ejecuciones/${id}`),
    enabled: Boolean(id),
  });

function useInvalidarEjecuciones() {
  const cliente = useQueryClient();
  return () => cliente.invalidateQueries({ queryKey: claves.ejecuciones });
}

export function useEjecutarExacto() {
  const invalidar = useInvalidarEjecuciones();
  return useMutation({
    mutationFn: () => post<EjecucionCreada>("/optimizacion/exacto"),
    onSuccess: invalidar,
  });
}

export function useEjecutarGenetico() {
  const invalidar = useInvalidarEjecuciones();
  return useMutation({
    mutationFn: (parametros: ParametrosAG) =>
      post<EjecucionCreada>("/optimizacion/genetico", parametros, 120_000),
    onSuccess: invalidar,
  });
}

export function useCalcularRangos() {
  const cliente = useQueryClient();
  return useMutation({
    mutationFn: (ejecucionId: string) =>
      post<Rangos>(`/sensibilidad/rangos/${ejecucionId}`, undefined, 120_000),
    onSuccess: (rangos) =>
      cliente.invalidateQueries({ queryKey: claves.ejecucion(rangos.ejecucion_id) }),
  });
}

// ---------- Sensibilidad ----------

export const useTornado = (porcentaje: number) =>
  useQuery({
    queryKey: claves.tornado(porcentaje),
    queryFn: () => get<Tornado>("/sensibilidad/tornado", { porcentaje }),
  });

export const useEscenarios = () =>
  useQuery({ queryKey: claves.escenarios, queryFn: () => get<Escenario[]>("/escenarios") });

export function useCrearEscenario() {
  const cliente = useQueryClient();
  return useMutation({
    mutationFn: (entrada: { nombre: string; descripcion?: string; ajustes: Ajuste[] }) =>
      post<Escenario>("/escenarios", entrada),
    onSuccess: () => cliente.invalidateQueries({ queryKey: claves.escenarios }),
  });
}

export function useEliminarEscenario() {
  const cliente = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/escenarios/${id}`),
    onSuccess: () => cliente.invalidateQueries({ queryKey: claves.escenarios }),
  });
}

export function useEjecutarEscenario() {
  const invalidar = useInvalidarEjecuciones();
  return useMutation({
    mutationFn: ({ id, incluirAg }: { id: string; incluirAg: boolean }) =>
      post<ResultadoEscenario>(
        `/escenarios/${id}/ejecutar`,
        { incluir_ag: incluirAg, parametros_ag: { semilla: 42 } },
        180_000,
      ),
    onSuccess: invalidar,
  });
}

// ---------- Análisis comparativo y de escalabilidad ----------

export const useListaAnalisis = (tipo?: string) =>
  useQuery({
    queryKey: [...claves.analisis, "lista", tipo],
    queryFn: () => get<AnalisisResumen[]>("/analisis", { tipo }),
  });

/** Consulta un análisis y la repite cada 1,5 s mientras siga en curso. */
export const useAnalisis = <R>(id: string | undefined) =>
  useQuery({
    queryKey: [...claves.analisis, id],
    queryFn: () => get<Analisis<R>>(`/analisis/${id}`),
    enabled: Boolean(id),
    refetchInterval: (consulta) => (consulta.state.data?.estado === "En curso" ? 1500 : false),
  });

export function useIniciarAnalisis() {
  const cliente = useQueryClient();
  return useMutation({
    mutationFn: ({ tipo, entrada }: { tipo: "comparacion" | "escalabilidad"; entrada: object }) =>
      post<Analisis>(`/analisis/${tipo}`, entrada),
    onSuccess: () => {
      cliente.invalidateQueries({ queryKey: claves.analisis });
      cliente.invalidateQueries({ queryKey: claves.ejecuciones });
    },
  });
}

// ---------- Descargas ----------

export function urlReporte(
  recurso: "ejecuciones" | "analisis",
  id: string,
  formato: "pdf" | "xlsx",
): string {
  return `${API_URL}/reportes/${recurso}/${id}.${formato}`;
}

export const URL_EXPORTAR_RED = `${API_URL}/datos/exportar`;
