from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ParametroGlobal


def obtener_valor(sesion: Session, clave: str) -> float:
    consulta = select(ParametroGlobal.valor).where(ParametroGlobal.clave == clave)
    valor = sesion.execute(consulta).scalar_one_or_none()
    if valor is None:
        raise LookupError(f"Falta el parámetro global '{clave}'")
    return float(valor)
