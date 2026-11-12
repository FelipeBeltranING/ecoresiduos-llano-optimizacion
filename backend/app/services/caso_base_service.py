import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Nodo, TipoNodo
from app.repositories import nodo_repository, ruta_repository
from app.schemas.datos import ResumenAcopios, ResumenCasoBase
from app.services import caso_real_service
from app.services.caso_base_datos import (
    ACOPIOS,
    COSTO_KM_CONSOLIDADO,
    DISTANCIAS_KM,
    EMPRESAS,
    ORDEN_PLANTAS,
    PLANTAS,
)
from app.services.distancias import FUENTE_ESTIMADA, distancia_vial_estimada


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
        ids = {**ids_empresas, **ids_plantas}
        sesion.flush()
        caso_real_service.completar_geometrias_caso_base(sesion, ids)
        caso_real_service.activar_solo(sesion, set(ids))
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise

    return ResumenCasoBase(
        empresas=len(EMPRESAS), plantas=len(PLANTAS), rutas=len(EMPRESAS) * len(PLANTAS)
    )


# Distancia vial estimada entre dos nodos (Haversine x 1,3): resultado reproducible
def distancia_entre(origen: Nodo, destino: Nodo) -> float:
    return distancia_vial_estimada(
        float(origen.latitud),
        float(origen.longitud),
        float(destino.latitud),
        float(destino.longitud),
    )


# Agrega los centros de acopio a la red activa con sus rutas (HU-17)
def cargar_acopios(sesion: Session) -> ResumenAcopios:
    rutas = 0
    try:
        empresas = nodos_activos(sesion, TipoNodo.FUENTE)
        plantas = nodos_activos(sesion, TipoNodo.PLANTA)
        for acopio in ACOPIOS:
            datos = {**acopio, "tipo": TipoNodo.ACOPIO, "tipo_residuo": None, "oferta_t": None}
            nodo_repository.guardar_nodo_por_codigo(sesion, {**datos, "activo": True})
            nodo = sesion.execute(select(Nodo).where(Nodo.codigo == acopio["codigo"])).scalar_one()
            # Paso 1: cada empresa puede llevar su residuo al acopio (flete directo)
            for empresa in empresas:
                medida = {"distancia_km": distancia_entre(empresa, nodo)}
                guardar_ruta_estimada(sesion, empresa.id, nodo.id, medida)
                rutas += 1
            # Paso 2: el acopio despacha a cada planta con flete consolidado
            for planta in plantas:
                medida = {
                    "distancia_km": distancia_entre(nodo, planta),
                    "costo_km_t": COSTO_KM_CONSOLIDADO,
                }
                guardar_ruta_estimada(sesion, nodo.id, planta.id, medida)
                rutas += 1
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    return ResumenAcopios(acopios=len(ACOPIOS), rutas=rutas)


def nodos_activos(sesion: Session, tipo: TipoNodo) -> list[Nodo]:
    consulta = select(Nodo).where(Nodo.tipo == tipo, Nodo.activo.is_(True)).order_by(Nodo.codigo)
    return list(sesion.execute(consulta).scalars())


def guardar_ruta_estimada(sesion: Session, origen_id, destino_id, medida: dict) -> None:
    datos = {**medida, "fuente_distancia": FUENTE_ESTIMADA}
    caso_real_service.guardar_ruta_completa(sesion, origen_id, destino_id, datos)
