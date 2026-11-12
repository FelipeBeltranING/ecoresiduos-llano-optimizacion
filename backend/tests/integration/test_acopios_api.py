from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from tests.utilidades import Z_OPTIMO_CASO_BASE, Z_OPTIMO_CON_ACOPIOS

ACOPIOS = "(SELECT id FROM nodo WHERE codigo IN ('A01', 'A02'))"


# Caso base con acopios; al final se borran para no afectar a las demás pruebas
@pytest.fixture
def cliente(cliente_pruebas: TestClient, motor_pruebas: Engine) -> Iterator[TestClient]:
    cliente_pruebas.post("/api/v1/datos/caso-base")
    yield cliente_pruebas
    with motor_pruebas.begin() as conexion:
        conexion.execute(
            text(
                f"DELETE FROM flujo_resultado WHERE origen_id IN {ACOPIOS} "
                f"OR destino_id IN {ACOPIOS}"
            )
        )
        conexion.execute(text(f"DELETE FROM sensibilidad_resultado WHERE nodo_id IN {ACOPIOS}"))
        conexion.execute(text("DELETE FROM nodo WHERE codigo IN ('A01', 'A02')"))


def test_cargar_acopios_y_optimizar(cliente: TestClient) -> None:
    respuesta = cliente.post("/api/v1/datos/acopios")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"acopios": 2, "rutas": 28}

    exacto = cliente.post("/api/v1/optimizacion/exacto").json()
    assert exacto["costo_total"] == pytest.approx(Z_OPTIMO_CON_ACOPIOS, abs=1)

    detalle = cliente.get(f"/api/v1/ejecuciones/{exacto['id']}").json()
    assert detalle["violaciones"] == 0
    destinos = {f["destino"] for f in detalle["flujos"]}
    origenes = {f["origen"] for f in detalle["flujos"]}
    assert {"A01", "A02"} <= destinos
    assert {"A01", "A02"} <= origenes


def test_ag_con_acopios_desde_la_api(cliente: TestClient) -> None:
    cliente.post("/api/v1/datos/acopios")
    respuesta = cliente.post("/api/v1/optimizacion/genetico", json={"semilla": 42})
    assert respuesta.status_code == 201
    detalle = cliente.get(f"/api/v1/ejecuciones/{respuesta.json()['id']}").json()
    assert detalle["violaciones"] == 0


def test_recargar_el_caso_base_desactiva_los_acopios(cliente: TestClient) -> None:
    cliente.post("/api/v1/datos/acopios")
    cliente.post("/api/v1/datos/caso-base")
    exacto = cliente.post("/api/v1/optimizacion/exacto").json()
    assert exacto["costo_total"] == pytest.approx(Z_OPTIMO_CASO_BASE, abs=1)
