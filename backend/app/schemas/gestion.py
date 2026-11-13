import uuid

from pydantic import BaseModel, Field, model_validator

from app.db.models import TipoNodo


class NodoBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    municipio: str = Field(min_length=2, max_length=80)
    tipo_residuo: str | None = Field(default=None, max_length=60)
    oferta_t: float | None = Field(default=None, ge=0)
    capacidad_t: float | None = Field(default=None, gt=0)
    costo_operacion_t: float = Field(default=0, ge=0)
    latitud: float = Field(ge=-4.5, le=13.5)
    longitud: float = Field(ge=-82, le=-66)


class NodoEntrada(NodoBase):
    codigo: str = Field(min_length=2, max_length=10, pattern=r"^[A-Z0-9_-]+$")
    tipo: TipoNodo

    @model_validator(mode="after")
    def revisar_por_tipo(self) -> "NodoEntrada":
        if self.tipo == TipoNodo.FUENTE and self.oferta_t is None:
            raise ValueError("Una empresa agropecuaria necesita su oferta semanal (oferta_t)")
        if self.tipo in (TipoNodo.PLANTA, TipoNodo.ACOPIO) and self.capacidad_t is None:
            raise ValueError("Una planta o centro de acopio necesita su capacidad (capacidad_t)")
        return self


class NodoActualizacion(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    municipio: str | None = Field(default=None, min_length=2, max_length=80)
    tipo_residuo: str | None = Field(default=None, max_length=60)
    oferta_t: float | None = Field(default=None, ge=0)
    capacidad_t: float | None = Field(default=None, gt=0)
    costo_operacion_t: float | None = Field(default=None, ge=0)
    latitud: float | None = Field(default=None, ge=-4.5, le=13.5)
    longitud: float | None = Field(default=None, ge=-82, le=-66)
    activo: bool | None = None


class NodoSalida(NodoBase):
    id: uuid.UUID
    codigo: str
    tipo: TipoNodo
    activo: bool


class RutaSalida(BaseModel):
    origen: str
    destino: str
    distancia_km: float | None
    costo_km_t: float | None
    habilitada: bool
    costo_unitario: float | None
    duracion_min: float | None = None
    fuente_distancia: str | None = None
    geometria: str | None = None


class MatrizRutas(BaseModel):
    origenes: list[str]
    destinos: list[str]
    rutas: list[RutaSalida]


class RutaCambio(BaseModel):
    origen: str
    destino: str
    distancia_km: float | None = Field(default=None, gt=0)
    costo_km_t: float | None = Field(default=None, ge=0)
    habilitada: bool | None = None
    quitar_costo_km_t: bool = False


class ResumenLote(BaseModel):
    actualizadas: int
    creadas: int


class ParametroSalida(BaseModel):
    clave: str
    valor: float
    unidad: str | None
    descripcion: str | None


class ParametroCambio(BaseModel):
    valor: float = Field(ge=0)


class ErrorImportacion(BaseModel):
    hoja: str
    fila: int
    mensaje: str


class ResumenImportacion(BaseModel):
    importado: bool
    empresas: int = 0
    plantas: int = 0
    acopios: int = 0
    rutas: int = 0
    errores: list[ErrorImportacion] = []
