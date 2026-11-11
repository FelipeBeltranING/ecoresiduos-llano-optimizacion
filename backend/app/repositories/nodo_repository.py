import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import Nodo, TipoNodo


# Inserta o actualiza un nodo usando su código
def guardar_nodo_por_codigo(sesion: Session, datos: dict) -> uuid.UUID:
    sentencia = insert(Nodo).values(**datos)

    columnas_a_actualizar = {}
    for columna, valor in datos.items():
        if columna != "codigo":
            columnas_a_actualizar[columna] = valor
    columnas_a_actualizar["actualizado_en"] = func.now()

    sentencia = sentencia.on_conflict_do_update(
        index_elements=["codigo"], set_=columnas_a_actualizar
    )
    sentencia = sentencia.returning(Nodo.id)
    return sesion.execute(sentencia).scalar_one()


# Cantidad de nodos de un tipo
def contar_nodos_por_tipo(sesion: Session, tipo: TipoNodo) -> int:
    consulta = select(func.count()).select_from(Nodo).where(Nodo.tipo == tipo)
    return sesion.execute(consulta).scalar_one()
