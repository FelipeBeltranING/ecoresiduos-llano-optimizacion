from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import SesionDB
from app.schemas.gestion import MatrizRutas, ResumenLote, RutaCambio
from app.services import gestion_service
from app.services.gestion_service import ConflictoError, NoEncontradoError

router = APIRouter(prefix="/rutas", tags=["rutas"])


# Matriz de distancias y costos unitarios (HU-03)
@router.get("/matriz", response_model=MatrizRutas)
def obtener_matriz(sesion: SesionDB) -> MatrizRutas:
    return gestion_service.obtener_matriz(sesion)


# Actualización por lote de distancias, costos por t·km y habilitación
@router.put("", response_model=ResumenLote)
def actualizar_lote(cambios: list[RutaCambio], sesion: SesionDB) -> ResumenLote:
    try:
        return gestion_service.actualizar_rutas(sesion, cambios)
    except NoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ConflictoError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(error)) from error


# Crea las rutas que faltan con distancia vial estimada
@router.post("/generar-faltantes", response_model=ResumenLote)
def generar_faltantes(sesion: SesionDB) -> ResumenLote:
    return gestion_service.generar_rutas_faltantes(sesion)
