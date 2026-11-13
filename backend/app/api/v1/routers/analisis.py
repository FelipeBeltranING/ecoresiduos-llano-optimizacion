import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status

from app.api.dependencias import SesionDB
from app.db.models.analisis import TIPO_COMPARACION, TIPO_ESCALABILIDAD
from app.schemas.analisis import (
    AnalisisResumen,
    AnalisisSalida,
    ComparacionEntrada,
    EscalabilidadEntrada,
)
from app.services import analisis_service
from app.services.analisis_service import AnalisisNoEncontradoError
from app.services.ejecucion_service import RedNoValidaError

router = APIRouter(prefix="/analisis", tags=["analisis"])


def lanzar(
    tipo: str,
    entrada: ComparacionEntrada | EscalabilidadEntrada,
    sesion: SesionDB,
    tareas: BackgroundTasks,
) -> AnalisisSalida:
    try:
        analisis = analisis_service.iniciar(sesion, tipo, entrada)
    except AnalisisNoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except RedNoValidaError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=error.mensajes) from error
    tareas.add_task(
        analisis_service.TAREAS[tipo],
        sesion.get_bind(),
        analisis.id,
        entrada.model_dump(mode="json"),
    )
    return analisis_service.a_salida(analisis)


@router.post("/comparacion", response_model=AnalisisSalida, status_code=status.HTTP_202_ACCEPTED)
def comparar(
    sesion: SesionDB, tareas: BackgroundTasks, entrada: ComparacionEntrada | None = None
) -> AnalisisSalida:
    return lanzar(TIPO_COMPARACION, entrada or ComparacionEntrada(), sesion, tareas)


@router.post("/escalabilidad", response_model=AnalisisSalida, status_code=status.HTTP_202_ACCEPTED)
def escalabilidad(
    sesion: SesionDB, tareas: BackgroundTasks, entrada: EscalabilidadEntrada | None = None
) -> AnalisisSalida:
    return lanzar(TIPO_ESCALABILIDAD, entrada or EscalabilidadEntrada(), sesion, tareas)


@router.get("", response_model=list[AnalisisResumen])
def listar(
    sesion: SesionDB,
    tipo: str | None = None,
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[AnalisisResumen]:
    return analisis_service.listar(sesion, tipo, limite)


@router.get("/{analisis_id}", response_model=AnalisisSalida)
def obtener(analisis_id: uuid.UUID, sesion: SesionDB) -> AnalisisSalida:
    try:
        return analisis_service.obtener(sesion, analisis_id)
    except AnalisisNoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error)) from error
