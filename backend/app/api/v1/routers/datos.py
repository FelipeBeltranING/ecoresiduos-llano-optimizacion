from fastapi import APIRouter

from app.api.dependencias import SesionDB
from app.schemas.datos import ResumenCasoBase
from app.services import caso_base_service

router = APIRouter(prefix="/datos", tags=["datos"])


# Carga del caso base del Meta (10 empresas, 4 plantas y 40 rutas)
@router.post("/caso-base", response_model=ResumenCasoBase)
def cargar_caso_base(sesion: SesionDB) -> ResumenCasoBase:
    return caso_base_service.cargar_caso_base(sesion)
