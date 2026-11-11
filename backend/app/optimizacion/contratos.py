from dataclasses import dataclass, field

import numpy as np

from app.optimizacion.red import RedLogistica

ESTADO_OPTIMO = "Óptimo"


# Resultado del modelo exacto (HU-07)
@dataclass
class ResultadoExacto:
    estado: str
    costo_total: float
    flujos: np.ndarray
    duales_oferta: np.ndarray
    duales_capacidad: np.ndarray
    costos_reducidos: np.ndarray
    holguras: np.ndarray
    tiempo_ms: float


# Parámetros del Algoritmo Genético (HU-09)
@dataclass
class ParametrosAG:
    tamano_poblacion: int = 100
    generaciones: int = 300
    prob_cruce: float = 0.85
    prob_mutacion: float = 0.10
    elitismo: int = 2
    lambda_pen: float = 1_000_000
    semilla: int | None = None


# Mejor costo y costo promedio de una generación
@dataclass
class RegistroConvergencia:
    generacion: int
    mejor_costo: float
    costo_promedio: float


# Resultado del Algoritmo Genético (HU-09)
@dataclass
class ResultadoGenetico:
    costo_total: float
    flujos: np.ndarray
    violaciones: float
    convergencia: list[RegistroConvergencia] = field(default_factory=list)
    tiempo_ms: float = 0.0


# Punto de conexión del modelo exacto: aquí se llama a la implementación del equipo
def resolver_exacto(red: RedLogistica) -> ResultadoExacto:
    raise NotImplementedError(
        "El modelo exacto (HU-07) todavía no está implementado. "
        "Conéctelo en app/optimizacion/contratos.py, función resolver_exacto."
    )


# Punto de conexión del Algoritmo Genético: aquí se llama a la implementación del equipo
def ejecutar_genetico(red: RedLogistica, parametros: ParametrosAG) -> ResultadoGenetico:
    raise NotImplementedError(
        "El Algoritmo Genético (HU-09) todavía no está conectado. "
        "Conéctelo en app/optimizacion/contratos.py, función ejecutar_genetico."
    )
