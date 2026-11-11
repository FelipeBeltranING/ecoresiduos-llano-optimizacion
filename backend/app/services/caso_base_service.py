import uuid

from sqlalchemy.orm import Session

from app.db.models import TipoNodo
from app.repositories import nodo_repository, ruta_repository
from app.schemas.datos import ResumenCasoBase
from app.services.caso_base_datos import DISTANCIAS_KM, EMPRESAS, ORDEN_PLANTAS, PLANTAS


# Carga de las empresas
def cargar_empresas(sesion: Session) -> dict[str, uuid.UUID]:
    ids_empresas = {}
    for empresa in EMPRESAS:
        datos = dict(empresa)
        datos["tipo"] = TipoNodo.FUENTE
        datos["capacidad_t"] = None
        datos["costo_operacion_t"] = 0
        datos["activo"] = True
        ids_empresas[empresa["codigo"]] = nodo_repository.guardar_nodo_por_codigo(sesion, datos)
    return ids_empresas


# Carga de las plantas
def cargar_plantas(sesion: Session) -> dict[str, uuid.UUID]:
    ids_plantas = {}
    for planta in PLANTAS:
        datos = dict(planta)
        datos["tipo"] = TipoNodo.PLANTA
        datos["tipo_residuo"] = None
        datos["oferta_t"] = None
        datos["activo"] = True
        ids_plantas[planta["codigo"]] = nodo_repository.guardar_nodo_por_codigo(sesion, datos)
    return ids_plantas


# Carga de las rutas empresa → planta
def cargar_rutas(
    sesion: Session, ids_empresas: dict[str, uuid.UUID], ids_plantas: dict[str, uuid.UUID]
) -> None:
    for codigo_empresa, distancias in DISTANCIAS_KM.items():
        for posicion, codigo_planta in enumerate(ORDEN_PLANTAS):
            origen_id = ids_empresas[codigo_empresa]
            destino_id = ids_plantas[codigo_planta]
            distancia = distancias[posicion]
            ruta_repository.guardar_ruta(sesion, origen_id, destino_id, distancia)


# Carga completa en una sola transacción
def cargar_caso_base(sesion: Session) -> ResumenCasoBase:
    try:
        ids_empresas = cargar_empresas(sesion)
        ids_plantas = cargar_plantas(sesion)
        cargar_rutas(sesion, ids_empresas, ids_plantas)
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise

    return ResumenCasoBase(
        empresas=nodo_repository.contar_nodos_por_tipo(sesion, TipoNodo.FUENTE),
        plantas=nodo_repository.contar_nodos_por_tipo(sesion, TipoNodo.PLANTA),
        rutas=ruta_repository.contar_rutas(sesion),
    )
