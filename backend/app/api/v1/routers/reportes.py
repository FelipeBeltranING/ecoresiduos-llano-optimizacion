import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.api.dependencias import SesionDB
from app.reportes import generador
from app.services import analisis_service, ejecucion_service
from app.services.analisis_service import AnalisisNoEncontradoError

router = APIRouter(prefix="/reportes", tags=["reportes"])

TIPOS = {
    "pdf": "application/pdf",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def archivo(contenido: bytes, formato: str, nombre: str) -> Response:
    return Response(
        content=contenido,
        media_type=TIPOS[formato],
        headers={"Content-Disposition": f'attachment; filename="{nombre}.{formato}"'},
    )


# Exportación de una ejecución en PDF o Excel (HU-16)
@router.get("/ejecuciones/{ejecucion_id}.{formato}")
def reporte_ejecucion(
    ejecucion_id: uuid.UUID, formato: Literal["pdf", "xlsx"], sesion: SesionDB
) -> Response:
    detalle = ejecucion_service.obtener_detalle(sesion, ejecucion_id)
    if detalle is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="La ejecución no existe")
    if formato == "pdf":
        contenido = generador.pdf_ejecucion(detalle)
    else:
        contenido = generador.excel_ejecucion(detalle)
    return archivo(contenido, formato, f"ejecucion_{str(ejecucion_id)[:8]}")


# Exportación de un análisis comparativo o de escalabilidad (HU-16)
@router.get("/analisis/{analisis_id}.{formato}")
def reporte_analisis(
    analisis_id: uuid.UUID, formato: Literal["pdf", "xlsx"], sesion: SesionDB
) -> Response:
    try:
        analisis = analisis_service.obtener(sesion, analisis_id)
    except AnalisisNoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    if formato == "pdf":
        contenido = generador.pdf_analisis(analisis)
    else:
        contenido = generador.excel_analisis(analisis)
    return archivo(contenido, formato, f"{analisis.tipo.lower()}_{str(analisis_id)[:8]}")
