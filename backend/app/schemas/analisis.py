import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.db.models import Metodo
from app.schemas.optimizacion import ParametrosAGEntrada


# Reporte comparativo exacto vs. AG con N corridas (HU-13)
class ComparacionEntrada(BaseModel):
    corridas: int = Field(default=5, ge=1, le=30)
    escenario_id: uuid.UUID | None = None
    parametros_ag: ParametrosAGEntrada = ParametrosAGEntrada()


class Tamano(BaseModel):
    empresas: int = Field(ge=2, le=300)
    plantas: int = Field(ge=2, le=60)


# Escalabilidad con instancias sintéticas (HU-14)
class EscalabilidadEntrada(BaseModel):
    tamanos: list[Tamano] = Field(
        default=[
            Tamano(empresas=10, plantas=4),
            Tamano(empresas=25, plantas=8),
            Tamano(empresas=50, plantas=10),
            Tamano(empresas=100, plantas=20),
        ],
        min_length=1,
        max_length=8,
    )
    semilla: int = Field(default=7, ge=0)
    parametros_ag: ParametrosAGEntrada = ParametrosAGEntrada(
        tamano_poblacion=60, generaciones=150, semilla=7
    )


class AnalisisSalida(BaseModel):
    id: uuid.UUID
    tipo: str
    estado: str
    escenario_id: uuid.UUID | None
    parametros: dict | None
    resultado: dict | None
    creado_en: datetime


class AnalisisResumen(BaseModel):
    id: uuid.UUID
    tipo: str
    estado: str
    escenario_id: uuid.UUID | None
    creado_en: datetime


# Historial de ejecuciones con filtros y paginación (HU-15)
class EjecucionResumen(BaseModel):
    id: uuid.UUID
    metodo: Metodo
    estado: str
    costo_total: float | None
    tiempo_ms: float | None
    violaciones: float | None
    escenario_id: uuid.UUID | None
    escenario_nombre: str | None
    creado_en: datetime


class PaginaEjecuciones(BaseModel):
    total: int
    pagina: int
    tamano: int
    items: list[EjecucionResumen]
