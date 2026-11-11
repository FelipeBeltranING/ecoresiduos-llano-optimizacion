from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# Conexión a la base de datos
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# Clase base de los modelos ORM
class Base(DeclarativeBase):
    pass


# Sesión por petición para los endpoints
def get_db() -> Iterator[Session]:
    sesion = SessionLocal()
    try:
        yield sesion
    finally:
        sesion.close()
