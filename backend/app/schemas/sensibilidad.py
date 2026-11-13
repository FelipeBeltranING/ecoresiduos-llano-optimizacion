import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.optimizacion import ParametrosAGEntrada

TipoAjuste = Literal["COSTO_TRANSPORTE", "OFERTA", "CAPACIDAD", "COSTO_RUTA", "CERRAR_RUTA"]


class AjusteEntrada(BaseModel):
    tipo: TipoAjuste
    porcentaje: float = Field(default=0, ge=-100, le=500)
    objetivo: str | None = Field(default=None, max_length=30)


class EscenarioEntrada(BaseModel):
    nombre: str = Field(min_length=3, max_length=120)
    descripcion: str | None = Field(default=None, max_length=400)
    ajustes: list[AjusteEntrada] = Field(min_length=1)


class EscenarioSalida(EscenarioEntrada):
    id: uuid.UUID
    creado_en: datetime


class EjecutarEscenarioEntrada(BaseModel):
    parametros_ag: ParametrosAGEntrada = ParametrosAGEntrada(semilla=42)
    incluir_ag: bool = True


class CambioFlujo(BaseModel):
    origen: str
    destino: str
    toneladas_base: float
    toneladas_escenario: float


class ResultadoEscenario(BaseModel):
    escenario_id: uuid.UUID
    nombre: str
    costo_base: float
    costo_exacto: float
    variacion_porcentual: float
    ejecucion_exacto_id: uuid.UUID
    ejecucion_ag_id: uuid.UUID | None
    costo_ag: float | None
    gap_ag: float | None
    tiempo_exacto_ms: float
    tiempo_ag_ms: float | None
    usa_planta_ficticia: bool
    toneladas_ficticia: float
    cambios_flujo: list[CambioFlujo]


class RangoSalida(BaseModel):
    tipo: Literal["COSTO_RUTA", "CAPACIDAD", "OFERTA"]
    elemento: str
    valor: float
    inferior: float | None
    superior: float | None
    dual_o_costo_reducido: float | None = None


class RangosSalida(BaseModel):
    ejecucion_id: uuid.UUID
    rangos: list[RangoSalida]
    omitido: str | None = None


class ImpactoSalida(BaseModel):
    parametro: str
    costo_menos: float | None
    costo_mas: float | None


class TornadoSalida(BaseModel):
    porcentaje: float
    costo_base: float
    impactos: list[ImpactoSalida]
