from pydantic import BaseModel


class CriticidadNodoSalida(BaseModel):
    codigo: str
    nombre: str | None = None
    tipo: str
    intermediacion: float
    grado_entrada: float
    resiliencia: float
    mecanismos: dict[str, bool]
    ice: float
    ranking_ice: int
    delta_costo_pct: float
    toneladas_sin_planta: float
    ranking_impacto: int


class CriticidadSalida(BaseModel):
    alfa: float
    beta: float
    gamma: float
    costo_base: float
    nodos: list[CriticidadNodoSalida]
    spearman: float | None
    pesos_calibrados: list[float] | None
    spearman_calibrado: float | None
    notas: list[str]
    referencia: str
