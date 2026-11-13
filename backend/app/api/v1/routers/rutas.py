from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import SesionDB
from app.schemas.gestion import MatrizRutas, ResumenLote, RutaCambio
from app.services import gestion_service
from app.services.gestion_service import ConflictoError, NoEncontradoError

router = APIRouter(prefix="/rutas", tags=["rutas"])


@router.get("/matriz", response_model=MatrizRutas)
def obtener_matriz(sesion: SesionDB) -> MatrizRutas:
    return gestion_service.obtener_matriz(sesion)


@router.put("", response_model=ResumenLote)
def actualizar_lote(cambios: list[RutaCambio], sesion: SesionDB) -> ResumenLote:
    try:
        return gestion_service.actualizar_rutas(sesion, cambios)
    except NoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ConflictoError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.post("/generar-faltantes", response_model=ResumenLote)
def generar_faltantes(sesion: SesionDB) -> ResumenLote:
    return gestion_service.generar_rutas_faltantes(sesion)
