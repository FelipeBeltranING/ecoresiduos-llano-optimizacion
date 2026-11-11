from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import Response

from app.api.dependencias import SesionDB
from app.schemas.datos import ResumenCasoBase
from app.schemas.gestion import ResumenImportacion
from app.services import caso_base_service, importacion_service

router = APIRouter(prefix="/datos", tags=["datos"])

TIPO_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# Carga del caso base del Meta (10 empresas, 4 plantas y 40 rutas)
@router.post("/caso-base", response_model=ResumenCasoBase)
def cargar_caso_base(sesion: SesionDB) -> ResumenCasoBase:
    return caso_base_service.cargar_caso_base(sesion)


# Exportación de la red a Excel (HU-05)
@router.get("/exportar")
def exportar(sesion: SesionDB) -> Response:
    contenido = importacion_service.exportar_red(sesion)
    return Response(
        content=contenido,
        media_type=TIPO_EXCEL,
        headers={"Content-Disposition": 'attachment; filename="red_ecoresiduos.xlsx"'},
    )


# Importación desde Excel con validación por fila (HU-05)
@router.post("/importar", response_model=ResumenImportacion)
async def importar(sesion: SesionDB, archivo: Annotated[UploadFile, File()]) -> ResumenImportacion:
    contenido = await archivo.read()
    return importacion_service.importar_red(sesion, contenido)
