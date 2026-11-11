from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.core.config import settings
from app.db.models import Base

# Configuración de Alembic y logging
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# URL de la base: la de las pruebas si se pasa, si no la de DATABASE_URL
def obtener_url() -> str:
    url_pruebas = config.attributes.get("url")
    if url_pruebas:
        return url_pruebas
    return settings.database_url


# Migraciones sin conexión (genera SQL)
def correr_migraciones_offline() -> None:
    context.configure(
        url=obtener_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# Migraciones conectadas a la base
def correr_migraciones_online() -> None:
    motor = create_engine(obtener_url(), pool_pre_ping=True)
    with motor.connect() as conexion:
        context.configure(connection=conexion, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    motor.dispose()


if context.is_offline_mode():
    correr_migraciones_offline()
else:
    correr_migraciones_online()
