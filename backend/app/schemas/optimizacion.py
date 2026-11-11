import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.db.models import Metodo


# Parámetros del AG que llegan desde la interfaz (HU-09)
class ParametrosAGEntrada(BaseModel):
    tamano_poblacion: int = Field(default=100, ge=10)
    generaciones: int = Field(default=300, ge=1)
    prob_cruce: float = Field(default=0.85, ge=0, le=1)
    prob_mutacion: float = Field(default=0.10, ge=0, le=1)
    elitismo: int = Field(default=2, ge=0)
    lambda_pen: float | None = Field(default=None, gt=0)
    semilla: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def revisar_elitismo(self) -> "ParametrosAGEntrada":
        if self.elitismo >= self.tamano_poblacion:
            raise ValueError("El elitismo debe ser menor que el tamaño de la población")
        return self


# Resumen de una ejecución recién creada
class EjecucionCreada(BaseModel):
    id: uuid.UUID
    metodo: Metodo
    estado: str
    costo_total: float | None
    tiempo_ms: float | None


# Flujo de una ruta en el resultado
class FlujoSalida(BaseModel):
    origen: str
    destino: str
    toneladas: float
    costo_unitario: float


# Dual, holgura o costo reducido de un nodo o de una ruta
class SensibilidadSalida(BaseModel):
    tipo: str
    elemento: str
    valor: float
    rango_inf: float | None
    rango_sup: float | None


# Mejor costo y costo promedio de una generación del AG
class ConvergenciaSalida(BaseModel):
    generacion: int
    mejor_costo: float
    costo_promedio: float


# Detalle completo de una ejecución
class EjecucionDetalle(EjecucionCreada):
    parametros: dict | None
    creado_en: datetime
    flujos: list[FlujoSalida]
    sensibilidad: list[SensibilidadSalida]
    convergencia: list[ConvergenciaSalida]
