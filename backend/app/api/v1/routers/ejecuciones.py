import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencias import SesionDB
from app.db.models import Metodo
from app.schemas.analisis import PaginaEjecuciones
from app.schemas.optimizacion import EjecucionDetalle
from app.services import analisis_service, ejecucion_service

router = APIRouter(prefix="/ejecuciones", tags=["ejecuciones"])


@router.get("", response_model=PaginaEjecuciones)
def listar_ejecuciones(
    sesion: SesionDB,
    metodo: Metodo | None = None,
    escenario_id: uuid.UUID | None = None,
    solo_base: bool = False,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    pagina: Annotated[int, Query(ge=1)] = 1,
    tamano: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginaEjecuciones:
    return analisis_service.historial(
        sesion, metodo, escenario_id, solo_base, desde, hasta, pagina, tamano
    )


@router.get("/{ejecucion_id}", response_model=EjecucionDetalle)
def obtener_ejecucion(ejecucion_id: uuid.UUID, sesion: SesionDB) -> EjecucionDetalle:
    detalle = ejecucion_service.obtener_detalle(sesion, ejecucion_id)
    if detalle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="La ejecución no existe")
    return detalle
