import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencias import SesionDB
from app.schemas.sensibilidad import (
    EjecutarEscenarioEntrada,
    EscenarioEntrada,
    EscenarioSalida,
    RangosSalida,
    ResultadoEscenario,
    TornadoSalida,
)
from app.services import sensibilidad_service
from app.services.ejecucion_service import RedNoValidaError
from app.services.sensibilidad_service import EscenarioInvalidoError, EscenarioNoEncontradoError

router = APIRouter(tags=["sensibilidad"])


def traducir_error(error: Exception) -> HTTPException:
    if isinstance(error, EscenarioNoEncontradoError):
        return HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, RedNoValidaError):
        return HTTPException(status.HTTP_409_CONFLICT, detail=error.mensajes)
    return HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error))


ERRORES = (EscenarioNoEncontradoError, EscenarioInvalidoError, RedNoValidaError)


@router.get("/escenarios", response_model=list[EscenarioSalida])
def listar_escenarios(sesion: SesionDB) -> list[EscenarioSalida]:
    return sensibilidad_service.listar_escenarios(sesion)


@router.post("/escenarios", response_model=EscenarioSalida, status_code=status.HTTP_201_CREATED)
def crear_escenario(entrada: EscenarioEntrada, sesion: SesionDB) -> EscenarioSalida:
    try:
        return sensibilidad_service.crear_escenario(sesion, entrada)
    except ERRORES as error:
        raise traducir_error(error) from error


@router.get("/escenarios/{escenario_id}", response_model=EscenarioSalida)
def obtener_escenario(escenario_id: uuid.UUID, sesion: SesionDB) -> EscenarioSalida:
    try:
        return sensibilidad_service.a_salida(
            sensibilidad_service.buscar_escenario(sesion, escenario_id)
        )
    except ERRORES as error:
        raise traducir_error(error) from error


@router.delete("/escenarios/{escenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_escenario(escenario_id: uuid.UUID, sesion: SesionDB) -> None:
    try:
        sensibilidad_service.eliminar_escenario(sesion, escenario_id)
    except ERRORES as error:
        raise traducir_error(error) from error


@router.post("/escenarios/{escenario_id}/ejecutar", response_model=ResultadoEscenario)
def ejecutar_escenario(
    escenario_id: uuid.UUID, sesion: SesionDB, entrada: EjecutarEscenarioEntrada | None = None
) -> ResultadoEscenario:
    try:
        return sensibilidad_service.ejecutar_escenario(
            sesion, escenario_id, entrada or EjecutarEscenarioEntrada()
        )
    except ERRORES as error:
        raise traducir_error(error) from error


@router.post("/sensibilidad/rangos/{ejecucion_id}", response_model=RangosSalida)
def calcular_rangos(ejecucion_id: uuid.UUID, sesion: SesionDB) -> RangosSalida:
    try:
        return sensibilidad_service.calcular_rangos_de_ejecucion(sesion, ejecucion_id)
    except ERRORES as error:
        raise traducir_error(error) from error


@router.get("/sensibilidad/tornado", response_model=TornadoSalida)
def calcular_tornado(
    sesion: SesionDB, porcentaje: Annotated[float, Query(gt=0, le=90)] = 20
) -> TornadoSalida:
    try:
        return sensibilidad_service.calcular_tornado(sesion, porcentaje)
    except ERRORES as error:
        raise traducir_error(error) from error
