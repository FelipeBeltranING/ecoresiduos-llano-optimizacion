from fastapi import APIRouter

from app.api.dependencias import SesionDB
from app.schemas.red import ValidacionRedRespuesta
from app.services import ejecucion_service

router = APIRouter(prefix="/red", tags=["red"])


@router.get("/validacion", response_model=ValidacionRedRespuesta)
def validar_red(sesion: SesionDB) -> ValidacionRedRespuesta:
    resultado = ejecucion_service.validar_red(sesion)
    return ValidacionRedRespuesta(
        es_valida=resultado.es_valida(),
        oferta_total=resultado.oferta_total,
        capacidad_total=resultado.capacidad_total,
        holgura_capacidad=resultado.holgura_capacidad,
        necesita_planta_ficticia=resultado.necesita_planta_ficticia,
        capacidad_ficticia=resultado.capacidad_ficticia,
        costo_ficticia=resultado.costo_ficticia,
        nodos_aislados=resultado.nodos_aislados,
        mensajes=resultado.mensajes,
    )
