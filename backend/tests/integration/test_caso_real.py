from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente(cliente_pruebas: TestClient) -> Iterator[TestClient]:
    yield cliente_pruebas
    cliente_pruebas.post("/api/v1/datos/caso-base")


def test_caso_real_reemplaza_la_red_activa(cliente: TestClient) -> None:
    resumen = cliente.post("/api/v1/datos/caso-real").json()

    assert resumen == {"empresas": 12, "plantas": 4, "rutas": 48}
    activos = [n for n in cliente.get("/api/v1/nodos").json() if n["activo"]]
    assert {n["codigo"][0] for n in activos} == {"R"}
    validacion = cliente.get("/api/v1/red/validacion").json()
    assert validacion["es_valida"] is True


def test_rutas_reales_tienen_trazado_osrm(cliente: TestClient) -> None:
    cliente.post("/api/v1/datos/caso-real")

    matriz = cliente.get("/api/v1/rutas/matriz").json()

    assert len(matriz["rutas"]) == 48
    assert all(r["fuente_distancia"] == "OSRM" for r in matriz["rutas"])
    assert all(r["geometria"] for r in matriz["rutas"])
    assert all(r["distancia_km"] >= 5 for r in matriz["rutas"])


def test_exacto_resuelve_el_caso_real(cliente: TestClient) -> None:
    cliente.post("/api/v1/datos/caso-real")

    respuesta = cliente.post("/api/v1/optimizacion/exacto")

    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "Óptimo"


def test_caso_base_recupera_su_red_con_trazados(cliente: TestClient) -> None:
    cliente.post("/api/v1/datos/caso-real")
    cliente.post("/api/v1/datos/caso-base")

    validacion = cliente.get("/api/v1/red/validacion").json()
    matriz = cliente.get("/api/v1/rutas/matriz").json()

    assert validacion["oferta_total"] == 890
    assert sum(1 for r in matriz["rutas"] if r["geometria"]) == 40


def test_fuentes_del_caso_real(cliente: TestClient) -> None:
    fuentes = cliente.get("/api/v1/datos/caso-real/fuentes").json()

    assert fuentes["coeficientes"]["tusa_por_rff"] == 0.22
    assert len(fuentes["empresas"]) == 12
