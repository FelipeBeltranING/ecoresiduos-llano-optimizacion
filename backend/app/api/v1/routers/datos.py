from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import Response

from app.api.dependencias import SesionDB
from app.schemas.datos import ResumenAcopios, ResumenCasoBase
from app.schemas.gestion import ResumenImportacion
from app.services import caso_base_service, caso_real_service, importacion_service

router = APIRouter(prefix="/datos", tags=["datos"])

TIPO_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# Carga del caso base del Meta (10 empresas, 4 plantas y 40 rutas)
@router.post("/caso-base", response_model=ResumenCasoBase)
def cargar_caso_base(sesion: SesionDB) -> ResumenCasoBase:
    return caso_base_service.cargar_caso_base(sesion)


# Centros de acopio de Puerto López y San Martín sobre la red activa (HU-17)
@router.post("/acopios", response_model=ResumenAcopios)
def cargar_acopios(sesion: SesionDB) -> ResumenAcopios:
    return caso_base_service.cargar_acopios(sesion)


# Carga del caso real del Meta: EVA 2018, ICA/FNG 2025, DIVIPOLA y rutas OSRM (HU-19)
@router.post("/caso-real", response_model=ResumenCasoBase)
def cargar_caso_real(sesion: SesionDB) -> ResumenCasoBase:
    return caso_real_service.cargar_caso_real(sesion)


# Fuentes y coeficientes del caso real, para mostrarlos en la interfaz y el informe
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
