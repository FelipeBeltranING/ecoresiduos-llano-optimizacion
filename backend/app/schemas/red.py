from pydantic import BaseModel


class ValidacionRedRespuesta(BaseModel):
    es_valida: bool
    oferta_total: float
    capacidad_total: float
    holgura_capacidad: float
    necesita_planta_ficticia: bool
    capacidad_ficticia: float
    costo_ficticia: float
    nodos_aislados: list[str]
    mensajes: list[str]
