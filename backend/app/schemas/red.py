from pydantic import BaseModel


# Respuesta de la validación de la red (HU-06)
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
