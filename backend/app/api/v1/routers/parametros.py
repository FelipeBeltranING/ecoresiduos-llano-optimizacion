from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import SesionDB
from app.schemas.gestion import ParametroCambio, ParametroSalida
from app.services import gestion_service
from app.services.gestion_service import ConflictoError, NoEncontradoError

router = APIRouter(prefix="/parametros", tags=["parametros"])


# Coeficientes del negocio (HU-04)
@router.get("", response_model=list[ParametroSalida])
def listar(sesion: SesionDB) -> list[ParametroSalida]:
    return gestion_service.listar_parametros(sesion)


@router.put("/{clave}", response_model=ParametroSalida)
def actualizar(clave: str, cambio: ParametroCambio, sesion: SesionDB) -> ParametroSalida:
    try:
        return gestion_service.actualizar_parametro(sesion, clave, cambio.valor)
    except NoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ConflictoError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(error)) from error
