/** Tipos de la API v1 de EcoResiduos (espejo de los esquemas Pydantic del backend). */

export type TipoNodo = "FUENTE" | "ACOPIO" | "PLANTA";
export type Metodo = "EXACTO" | "GENETICO";

export interface Nodo {
  id: string;
  codigo: string;
  tipo: TipoNodo;
  nombre: string;
  municipio: string;
  tipo_residuo: string | null;
  oferta_t: number | null;
  capacidad_t: number | null;
  costo_operacion_t: number;
  latitud: number;
  longitud: number;
  activo: boolean;
}

export type NodoEntrada = Omit<Nodo, "id" | "activo">;
export type NodoCambios = Partial<Omit<Nodo, "id" | "codigo" | "tipo">>;

export interface Ruta {
  origen: string;
  destino: string;
  distancia_km: number | null;
  costo_km_t: number | null;
  habilitada: boolean;
  costo_unitario: number | null;
  duracion_min: number | null;
  fuente_distancia: string | null;
  geometria: string | null;
}

export interface MatrizRutas {
  origenes: string[];
  destinos: string[];
  rutas: Ruta[];
}

export interface RutaCambio {
  origen: string;
  destino: string;
  distancia_km?: number;
  costo_km_t?: number;
  habilitada?: boolean;
  quitar_costo_km_t?: boolean;
}

export interface Parametro {
  clave: string;
  valor: number;
  unidad: string | null;
  descripcion: string | null;
}

export interface Validacion {
  es_valida: boolean;
  oferta_total: number;
  capacidad_total: number;
  holgura_capacidad: number;
  necesita_planta_ficticia: boolean;
  capacidad_ficticia: number;
  costo_ficticia: number;
  nodos_aislados: string[];
  mensajes: string[];
}

export interface ResumenCaso {
  empresas: number;
  plantas: number;
  rutas: number;
}

export interface ResumenImportacion {
  importado: boolean;
  empresas: number;
  plantas: number;
  acopios: number;
  rutas: number;
  errores: { hoja: string; fila: number; mensaje: string }[];
}

export interface FuentesCasoReal {
  descripcion: string;
  coeficientes: Record<string, number | Record<string, number>>;
  empresas: {
    codigo: string;
    municipio: string;
    produccion: number;
    unidad: string;
    residuo_anual_t: number;
    captacion: number;
  }[];
}

export interface ParametrosAG {
  tamano_poblacion: number;
  generaciones: number;
  prob_cruce: number;
  prob_mutacion: number;
  elitismo: number;
  lambda_pen?: number | null;
  semilla?: number | null;
  tipo_seleccion: "torneo" | "ruleta";
  tipo_cruce: "un_punto" | "dos_puntos";
}

export interface EjecucionCreada {
  id: string;
  metodo: Metodo;
  estado: string;
  costo_total: number | null;
  tiempo_ms: number | null;
}

export interface Flujo {
  origen: string;
  destino: string;
  toneladas: number;
  costo_unitario: number;
}

export interface Sensibilidad {
  tipo: "DUAL_OFERTA" | "DUAL_CAPACIDAD" | "HOLGURA_CAPACIDAD" | "COSTO_REDUCIDO";
  elemento: string;
  valor: number;
  rango_inf: number | null;
  rango_sup: number | null;
}

export interface Convergencia {
  generacion: number;
  mejor_costo: number;
  costo_promedio: number;
}

export interface EjecucionDetalle extends EjecucionCreada {
  violaciones: number | null;
  escenario_id: string | null;
  parametros: Partial<ParametrosAG> | null;
  creado_en: string;
  flujos: Flujo[];
  sensibilidad: Sensibilidad[];
  convergencia: Convergencia[];
}

export interface EjecucionResumen {
  id: string;
  metodo: Metodo;
  estado: string;
  costo_total: number | null;
  tiempo_ms: number | null;
  violaciones: number | null;
  escenario_id: string | null;
  escenario_nombre: string | null;
  creado_en: string;
}

export interface PaginaEjecuciones {
  total: number;
  pagina: number;
  tamano: number;
  items: EjecucionResumen[];
}

export type TipoAjuste = "COSTO_TRANSPORTE" | "OFERTA" | "CAPACIDAD" | "COSTO_RUTA" | "CERRAR_RUTA";

export interface Ajuste {
  tipo: TipoAjuste;
  porcentaje: number;
  objetivo: string | null;
}

export interface Escenario {
  id: string;
  nombre: string;
  descripcion: string | null;
  ajustes: Ajuste[];
  creado_en: string;
}

export interface ResultadoEscenario {
  escenario_id: string;
  nombre: string;
  costo_base: number;
  costo_exacto: number;
  variacion_porcentual: number;
  ejecucion_exacto_id: string;
  ejecucion_ag_id: string | null;
  costo_ag: number | null;
  gap_ag: number | null;
  tiempo_exacto_ms: number;
  tiempo_ag_ms: number | null;
  usa_planta_ficticia: boolean;
  toneladas_ficticia: number;
  cambios_flujo: {
    origen: string;
    destino: string;
    toneladas_base: number;
    toneladas_escenario: number;
  }[];
}

export interface Rango {
  tipo: "COSTO_RUTA" | "CAPACIDAD" | "OFERTA";
  elemento: string;
  valor: number;
  inferior: number | null;
  superior: number | null;
  dual_o_costo_reducido: number | null;
}

export interface Rangos {
  ejecucion_id: string;
  rangos: Rango[];
  omitido: string | null;
}

export interface Tornado {
  porcentaje: number;
  costo_base: number;
  impactos: { parametro: string; costo_menos: number | null; costo_mas: number | null }[];
}

export interface CorridaAG {
  semilla: number;
  costo: number;
  tiempo_ms: number;
  violaciones: number;
  generaciones: number;
  gap: number;
}

export interface ResultadoComparacion {
  exacto: {
    ejecucion_id: string;
    costo: number;
    tiempo_ms: number;
    violaciones: number;
    estado: string;
  };
  ag: {
    mejor_ejecucion_id: string;
    mejor: number;
    peor: number;
    promedio: number;
    desviacion: number;
    gap_mejor: number;
    gap_promedio: number;
    tiempo_promedio_ms: number;
    violaciones_max: number;
    corridas: CorridaAG[];
    convergencia_mejor: { generacion: number; mejor: number; promedio: number }[];
  };
  red: { empresas: number; plantas: number; usa_planta_ficticia: boolean };
}

export interface FilaEscalabilidad {
  empresas: number;
  plantas: number;
  variables: number;
  costo_exacto: number;
  tiempo_exacto_ms: number;
  costo_ag: number;
  tiempo_ag_ms: number;
  gap: number;
  violaciones_ag: number;
  generaciones_ag: number;
}

export interface Analisis<R = unknown> {
  id: string;
  tipo: "COMPARACION" | "ESCALABILIDAD";
  estado: "En curso" | "Terminado" | "Error";
  escenario_id: string | null;
  parametros: Record<string, unknown> | null;
  resultado: (R & { error?: string }) | null;
  creado_en: string;
}

export interface AnalisisResumen {
  id: string;
  tipo: "COMPARACION" | "ESCALABILIDAD";
  estado: string;
  escenario_id: string | null;
  creado_en: string;
}
