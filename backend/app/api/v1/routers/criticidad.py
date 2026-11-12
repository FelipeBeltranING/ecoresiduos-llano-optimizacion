from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencias import SesionDB
from app.schemas.criticidad import CriticidadSalida
from app.services import criticidad_service
from app.services.ejecucion_service import RedNoValidaError

router = APIRouter(prefix="/criticidad", tags=["criticidad"])

Peso = Annotated[float, Query(ge=0, le=1)]


# Índice de Criticidad Estructural de plantas y acopios (HU-20)
@router.get("", response_model=CriticidadSalida)
def calcular(
    sesion: SesionDB, alfa: Peso = 0.5, beta: Peso = 0.3, gamma: Peso = 0.2
) -> CriticidadSalida:
    if abs(alfa + beta + gamma - 1) > 1e-6:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, detail="alfa + beta + gamma debe ser 1"
        )
    try:
        return criticidad_service.analizar(sesion, alfa, beta, gamma)
    except RedNoValidaError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=error.mensajes) from error
    except ValueError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error
