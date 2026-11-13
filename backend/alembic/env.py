from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.core.config import settings
from app.db.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def obtener_url() -> str:
    url_pruebas = config.attributes.get("url")
    if url_pruebas:
        return url_pruebas
    return settings.database_url


def correr_migraciones_offline() -> None:
    context.configure(
        url=obtener_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


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
