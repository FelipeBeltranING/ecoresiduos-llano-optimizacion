from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.session import get_db
from app.main import app

CARPETA_BACKEND = Path(__file__).resolve().parents[2]


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if "integration" in str(item.path):
            item.add_marker(pytest.mark.integracion)


def obtener_url_pruebas() -> str:
    url = settings.test_database_url
    if not url:
        pytest.skip("TEST_DATABASE_URL no está definida")
    if "supabase" in url:
        pytest.exit("TEST_DATABASE_URL no puede apuntar a Supabase", returncode=1)
    return url


@pytest.fixture(scope="session")
def motor_pruebas() -> Iterator[Engine]:
    url = obtener_url_pruebas()

    configuracion = Config(str(CARPETA_BACKEND / "alembic.ini"))
    configuracion.attributes["url"] = url
    command.upgrade(configuracion, "head")

    motor = create_engine(url, pool_pre_ping=True)
    yield motor
    motor.dispose()


@pytest.fixture
def sesion_pruebas(motor_pruebas: Engine) -> Iterator[Session]:
    fabrica = sessionmaker(bind=motor_pruebas, autoflush=False, expire_on_commit=False)
    sesion = fabrica()
    try:
        yield sesion
    finally:
        sesion.rollback()
        sesion.close()


@pytest.fixture
def cliente_pruebas(motor_pruebas: Engine) -> Iterator[TestClient]:
    fabrica = sessionmaker(bind=motor_pruebas, autoflush=False, expire_on_commit=False)

    def obtener_sesion_pruebas() -> Iterator[Session]:
        sesion = fabrica()
        try:
            yield sesion
        finally:
            sesion.close()

    app.dependency_overrides[get_db] = obtener_sesion_pruebas
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()
