from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import SesionDB
from app.db.models import TipoNodo
from app.schemas.gestion import NodoActualizacion, NodoEntrada, NodoSalida
from app.services import gestion_service
from app.services.gestion_service import ConflictoError, NoEncontradoError

router = APIRouter(prefix="/nodos", tags=["nodos"])


@router.get("", response_model=list[NodoSalida])
def listar(
    sesion: SesionDB, tipo: TipoNodo | None = None, incluir_inactivos: bool = True
) -> list[NodoSalida]:
    return gestion_service.listar_nodos(sesion, tipo, incluir_inactivos)


@router.get("/{codigo}", response_model=NodoSalida)
def obtener(codigo: str, sesion: SesionDB) -> NodoSalida:
    try:
        return gestion_service.a_salida(gestion_service.buscar_nodo(sesion, codigo))
    except NoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post("", response_model=NodoSalida, status_code=status.HTTP_201_CREATED)
def crear(entrada: NodoEntrada, sesion: SesionDB) -> NodoSalida:
    try:
        return gestion_service.crear_nodo(sesion, entrada)
    except ConflictoError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.patch("/{codigo}", response_model=NodoSalida)
def actualizar(codigo: str, cambios: NodoActualizacion, sesion: SesionDB) -> NodoSalida:
    try:
        return gestion_service.actualizar_nodo(sesion, codigo, cambios)
    except NoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ConflictoError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.delete("/{codigo}", response_model=NodoSalida)
def desactivar(codigo: str, sesion: SesionDB) -> NodoSalida:
    try:
        return gestion_service.desactivar_nodo(sesion, codigo)
    except NoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error)) from error
