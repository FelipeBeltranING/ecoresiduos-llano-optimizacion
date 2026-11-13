from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import Response

from app.api.dependencias import SesionDB
from app.schemas.datos import ResumenAcopios, ResumenCasoBase
from app.schemas.gestion import ResumenImportacion
from app.services import caso_base_service, caso_real_service, importacion_service

router = APIRouter(prefix="/datos", tags=["datos"])

TIPO_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.post("/caso-base", response_model=ResumenCasoBase)
def cargar_caso_base(sesion: SesionDB) -> ResumenCasoBase:
    return caso_base_service.cargar_caso_base(sesion)


@router.post("/acopios", response_model=ResumenAcopios)
def cargar_acopios(sesion: SesionDB) -> ResumenAcopios:
    return caso_base_service.cargar_acopios(sesion)


@router.post("/caso-real", response_model=ResumenCasoBase)
def cargar_caso_real(sesion: SesionDB) -> ResumenCasoBase:
    return caso_real_service.cargar_caso_real(sesion)


@router.get("/caso-real/fuentes")
def fuentes_caso_real() -> dict:
    caso = caso_real_service.leer_caso_real()
    return {
        "descripcion": caso["descripcion"],
        "coeficientes": caso["coeficientes"],
        "empresas": [
            {"codigo": e["codigo"], "municipio": e["municipio"], **e["fuente_dato"]}
            for e in caso["empresas"]
        ],
    }


@router.get("/exportar")
def exportar(sesion: SesionDB) -> Response:
    contenido = importacion_service.exportar_red(sesion)
    return Response(
        content=contenido,
        media_type=TIPO_EXCEL,
        headers={"Content-Disposition": 'attachment; filename="red_ecoresiduos.xlsx"'},
    )


@router.post("/importar", response_model=ResumenImportacion)
async def importar(sesion: SesionDB, archivo: Annotated[UploadFile, File()]) -> ResumenImportacion:
    contenido = await archivo.read()
    return importacion_service.importar_red(sesion, contenido)
