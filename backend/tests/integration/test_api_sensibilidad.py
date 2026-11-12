from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import Engine

AG_RAPIDO = {"parametros_ag": {"semilla": 1, "generaciones": 20, "tamano_poblacion": 30}}


@pytest.fixture
def cliente(cliente_pruebas: TestClient, motor_pruebas: Engine) -> Iterator[TestClient]:
    cliente_pruebas.post("/api/v1/datos/caso-base")
    yield cliente_pruebas
    with motor_pruebas.begin() as conexion:
        conexion.execute(text("DELETE FROM escenario WHERE nombre LIKE 'Prueba%'"))


def crear(cliente: TestClient, nombre: str, ajustes: list[dict]) -> str:
    respuesta = cliente.post("/api/v1/escenarios", json={"nombre": nombre, "ajustes": ajustes})
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def test_combustible_mas_20_por_ciento_sube_el_costo(cliente: TestClient) -> None:
    escenario_id = crear(
        cliente, "Prueba combustible", [{"tipo": "COSTO_TRANSPORTE", "porcentaje": 20}]
    )

    respuesta = cliente.post(f"/api/v1/escenarios/{escenario_id}/ejecutar", json=AG_RAPIDO)

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["costo_base"] == pytest.approx(64_691_000)
    assert cuerpo["variacion_porcentual"] > 0
    assert cuerpo["costo_ag"] >= cuerpo["costo_exacto"] - 1
    detalle = cliente.get(f"/api/v1/ejecuciones/{cuerpo['ejecucion_exacto_id']}").json()
    assert detalle["escenario_id"] == escenario_id
    assert detalle["violaciones"] == 0


def test_oferta_mas_10_por_ciento_usa_planta_ficticia(cliente: TestClient) -> None:
    escenario_id = crear(cliente, "Prueba oferta", [{"tipo": "OFERTA", "porcentaje": 10}])

    cuerpo = cliente.post(
        f"/api/v1/escenarios/{escenario_id}/ejecutar", json={"incluir_ag": False}
    ).json()

    assert cuerpo["usa_planta_ficticia"] is True
    assert cuerpo["toneladas_ficticia"] == pytest.approx(29)
    assert cuerpo["ejecucion_ag_id"] is None


def test_cuello_de_botella_en_una_planta(cliente: TestClient) -> None:
    escenario_id = crear(
        cliente, "Prueba cuello", [{"tipo": "CAPACIDAD", "porcentaje": -30, "objetivo": "P01"}]
    )

    cuerpo = cliente.post(
        f"/api/v1/escenarios/{escenario_id}/ejecutar", json={"incluir_ag": False}
    ).json()

    assert cuerpo["costo_exacto"] > cuerpo["costo_base"]
    assert any(c["destino"] == "P01" for c in cuerpo["cambios_flujo"])


def test_objetivo_inexistente_da_422(cliente: TestClient) -> None:
    respuesta = cliente.post(
        "/api/v1/escenarios",
        json={
            "nombre": "Prueba mala",
            "ajustes": [{"tipo": "CAPACIDAD", "porcentaje": -30, "objetivo": "P99"}],
        },
    )

    assert respuesta.status_code == 422


def test_rangos_de_estabilidad_del_exacto(cliente: TestClient) -> None:
    ejecucion_id = cliente.post("/api/v1/optimizacion/exacto").json()["id"]

    respuesta = cliente.post(f"/api/v1/sensibilidad/rangos/{ejecucion_id}")

    assert respuesta.status_code == 200
    rangos = respuesta.json()["rangos"]
    p01 = next(r for r in rangos if r["tipo"] == "CAPACIDAD" and r["elemento"] == "P01")
    assert p01["inferior"] <= 300 <= p01["superior"]
    assert p01["dual_o_costo_reducido"] == pytest.approx(-17750)
    detalle = cliente.get(f"/api/v1/ejecuciones/{ejecucion_id}").json()
    con_rango = [s for s in detalle["sensibilidad"] if s["rango_inf"] is not None]
    assert len(con_rango) > 0


def test_tornado_ordena_por_impacto(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/v1/sensibilidad/tornado", params={"porcentaje": 20})

    cuerpo = respuesta.json()
    assert cuerpo["costo_base"] == pytest.approx(64_691_000)
    assert cuerpo["impactos"][0]["parametro"] == "Oferta total"
