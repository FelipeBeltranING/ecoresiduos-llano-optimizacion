from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import SesionDB
from app.db.models import Ejecucion
from app.schemas.optimizacion import EjecucionCreada, ParametrosAGEntrada
from app.services import ejecucion_service
from app.services.ejecucion_service import RedNoValidaError

router = APIRouter(prefix="/optimizacion", tags=["optimizacion"])


# Respuesta común de una ejecución creada
def resumir(ejecucion: Ejecucion) -> EjecucionCreada:
    return EjecucionCreada(
        id=ejecucion.id,
        metodo=ejecucion.metodo,
        estado=ejecucion.estado,
        costo_total=ejecucion.costo_total,
        tiempo_ms=ejecucion.tiempo_ms,
    )


# Modelo exacto (HU-07)
@router.post("/exacto", response_model=EjecucionCreada, status_code=status.HTTP_201_CREATED)
def ejecutar_exacto(sesion: SesionDB) -> EjecucionCreada:
    try:
        ejecucion = ejecucion_service.ejecutar_exacto(sesion)
    except RedNoValidaError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=error.mensajes) from error
    except NotImplementedError as error:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail=str(error)) from error
    return resumir(ejecucion)


# Algoritmo Genético (HU-09)
@router.post("/genetico", response_model=EjecucionCreada, status_code=status.HTTP_201_CREATED)
def ejecutar_genetico(sesion: SesionDB, parametros: ParametrosAGEntrada) -> EjecucionCreada:
    try:
        ejecucion = ejecucion_service.ejecutar_genetico(sesion, parametros)
    except RedNoValidaError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=error.mensajes) from error
    except NotImplementedError as error:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail=str(error)) from error
    return resumir(ejecucion)
