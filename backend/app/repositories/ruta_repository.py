import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import Ruta


# Inserta o actualiza la ruta entre un origen y un destino
def guardar_ruta(
    sesion: Session, origen_id: uuid.UUID, destino_id: uuid.UUID, distancia_km: float
) -> None:
    sentencia = insert(Ruta).values(
        origen_id=origen_id,
        destino_id=destino_id,
        distancia_km=distancia_km,
        costo_km_t=None,
        habilitada=True,
    )
    sentencia = sentencia.on_conflict_do_update(
        index_elements=["origen_id", "destino_id"],
        set_={"distancia_km": distancia_km, "costo_km_t": None, "habilitada": True},
    )
    sesion.execute(sentencia)


# Cantidad total de rutas
def contar_rutas(sesion: Session) -> int:
    consulta = select(func.count()).select_from(Ruta)
    return sesion.execute(consulta).scalar_one()
