import json
from functools import lru_cache
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import Nodo, Ruta, TipoNodo
from app.repositories import nodo_repository
from app.schemas.datos import ResumenCasoBase
from app.services.distancias import FUENTE_ESTIMADA, FUENTE_OSRM

CARPETA_DATOS = Path(__file__).resolve().parent / "datos"


@lru_cache
def leer_caso_real() -> dict:
    return json.loads((CARPETA_DATOS / "caso_real_meta.json").read_text(encoding="utf-8"))


@lru_cache
def leer_geometrias_caso_base() -> dict[tuple[str, str], dict]:
    archivo = CARPETA_DATOS / "caso_base_geometrias.json"
    if not archivo.exists():
        return {}
    filas = json.loads(archivo.read_text(encoding="utf-8"))
    return {(f["origen"], f["destino"]): f for f in filas}


def activar_solo(sesion: Session, codigos: set[str]) -> None:
    sesion.execute(update(Nodo).where(Nodo.codigo.not_in(codigos)).values(activo=False))


def guardar_ruta_completa(sesion: Session, origen_id, destino_id, datos: dict) -> None:
    valores = {
        "origen_id": origen_id,
        "destino_id": destino_id,
        "distancia_km": datos["distancia_km"],
        "costo_km_t": datos.get("costo_km_t"),
        "habilitada": True,
        "geometria": datos.get("geometria"),
        "duracion_min": datos.get("duracion_min"),
        "fuente_distancia": datos.get("fuente_distancia"),
    }
    sentencia = insert(Ruta).values(**valores)
    sesion.execute(
        sentencia.on_conflict_do_update(
            index_elements=["origen_id", "destino_id"],
            set_={k: v for k, v in valores.items() if k not in ("origen_id", "destino_id")},
        )
    )


def cargar_caso_real(sesion: Session) -> ResumenCasoBase:
    caso = leer_caso_real()
    ids = {}
    try:
        for empresa in caso["empresas"]:
            datos = {k: v for k, v in empresa.items() if k != "fuente_dato"}
            datos.update(tipo=TipoNodo.FUENTE, capacidad_t=None, costo_operacion_t=0, activo=True)
            ids[empresa["codigo"]] = nodo_repository.guardar_nodo_por_codigo(sesion, datos)
        for planta in caso["plantas"]:
            datos = dict(planta)
            datos.update(tipo=TipoNodo.PLANTA, tipo_residuo=None, oferta_t=None, activo=True)
            ids[planta["codigo"]] = nodo_repository.guardar_nodo_por_codigo(sesion, datos)
        for ruta in caso["rutas"]:
            guardar_ruta_completa(
                sesion,
                ids[ruta["origen"]],
                ids[ruta["destino"]],
                {**ruta, "fuente_distancia": FUENTE_OSRM},
            )
        activar_solo(sesion, set(ids))
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    return ResumenCasoBase(
        empresas=len(caso["empresas"]),
        plantas=len(caso["plantas"]),
        rutas=len(caso["rutas"]),
    )


def completar_geometrias_caso_base(sesion: Session, ids: dict) -> None:
    geometrias = leer_geometrias_caso_base()
    for (origen, destino), fila in geometrias.items():
        if origen not in ids or destino not in ids:
            continue
        ruta = sesion.execute(
            select(Ruta).where(Ruta.origen_id == ids[origen], Ruta.destino_id == ids[destino])
        ).scalar_one_or_none()
        if ruta is not None:
            ruta.geometria = fila["geometria"]
            ruta.fuente_distancia = FUENTE_ESTIMADA
