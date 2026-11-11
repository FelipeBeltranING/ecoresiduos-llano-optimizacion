import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import SesionDB
from app.schemas.optimizacion import EjecucionDetalle
from app.services import ejecucion_service

router = APIRouter(prefix="/ejecuciones", tags=["ejecuciones"])


# Detalle de una ejecución
@router.get("/{ejecucion_id}", response_model=EjecucionDetalle)
def obtener_ejecucion(ejecucion_id: uuid.UUID, sesion: SesionDB) -> EjecucionDetalle:
    detalle = ejecucion_service.obtener_detalle(sesion, ejecucion_id)
    if detalle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="La ejecución no existe")
    return detalle
