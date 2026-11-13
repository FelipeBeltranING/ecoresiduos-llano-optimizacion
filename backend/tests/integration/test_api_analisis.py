import io

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook
from sqlalchemy import text
from sqlalchemy.engine import Engine

AG_RAPIDO = {"semilla": 3, "generaciones": 15, "tamano_poblacion": 20}


@pytest.fixture
def cliente(cliente_pruebas: TestClient) -> TestClient:
    cliente_pruebas.post("/api/v1/datos/caso-base")
    return cliente_pruebas


# En TestClient la tarea en segundo plano termina antes de devolver la respuesta
def test_comparacion_exacto_vs_ag(cliente: TestClient) -> None:
    creado = cliente.post(
        "/api/v1/analisis/comparacion", json={"corridas": 3, "parametros_ag": AG_RAPIDO}
    )
    assert creado.status_code == 202

    analisis = cliente.get(f"/api/v1/analisis/{creado.json()['id']}").json()

    assert analisis["estado"] == "Terminado", analisis["resultado"]
    resultado = analisis["resultado"]
    assert resultado["exacto"]["costo"] == pytest.approx(64_691_000)
    assert len(resultado["ag"]["corridas"]) == 3
    assert resultado["ag"]["gap_mejor"] >= -1e-6
    assert resultado["ag"]["mejor"] <= resultado["ag"]["promedio"] + 1e-6


def test_escalabilidad_con_instancias_sinteticas(cliente: TestClient) -> None:
    entrada = {
        "tamanos": [{"empresas": 10, "plantas": 4}, {"empresas": 30, "plantas": 6}],
        "parametros_ag": AG_RAPIDO,
    }

    creado = cliente.post("/api/v1/analisis/escalabilidad", json=entrada)

    analisis = cliente.get(f"/api/v1/analisis/{creado.json()['id']}").json()
    filas = analisis["resultado"]["filas"]
    assert [f["variables"] for f in filas] == [40, 180]
    assert all(f["gap"] >= -1e-6 for f in filas)
    assert all(f["violaciones_ag"] <= 1e-3 for f in filas)


def test_historial_filtra_por_metodo_y_pagina(cliente: TestClient) -> None:
    cliente.post("/api/v1/optimizacion/exacto")
    cliente.post("/api/v1/optimizacion/exacto")

    pagina = cliente.get(
        "/api/v1/ejecuciones", params={"metodo": "EXACTO", "tamano": 1, "pagina": 1}
    ).json()

    assert pagina["total"] >= 2
    assert len(pagina["items"]) == 1
    assert pagina["items"][0]["metodo"] == "EXACTO"


def test_reportes_pdf_y_excel(cliente: TestClient) -> None:
    ejecucion_id = cliente.post("/api/v1/optimizacion/exacto").json()["id"]

    pdf = cliente.get(f"/api/v1/reportes/ejecuciones/{ejecucion_id}.pdf")
    excel = cliente.get(f"/api/v1/reportes/ejecuciones/{ejecucion_id}.xlsx")

    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")
    libro = load_workbook(io.BytesIO(excel.content))
    assert {"Resumen", "Flujos", "Sensibilidad"} <= set(libro.sheetnames)


def test_comparacion_con_varios_escenarios(cliente: TestClient, motor_pruebas: Engine) -> None:
    escenario_alto = cliente.post(
        "/api/v1/escenarios",
        json={
            "nombre": "Prueba compuesto",
            "ajustes": [{"tipo": "COSTO_TRANSPORTE", "porcentaje": 20}],
        },
    ).json()["id"]
    escenario_bajo = cliente.post(
        "/api/v1/escenarios",
        json={
            "nombre": "Prueba capacidad",
            "ajustes": [{"tipo": "CAPACIDAD", "porcentaje": -20}],
        },
    ).json()["id"]
    try:
        creado = cliente.post(
            "/api/v1/analisis/comparacion",
            json={
                "corridas": 2,
                "escenarios": [escenario_alto, escenario_bajo],
                "parametros_ag": AG_RAPIDO,
            },
        ).json()

        analisis = cliente.get(f"/api/v1/analisis/{creado['id']}").json()

        assert analisis["estado"] == "Terminado", analisis["resultado"]
        filas = analisis["resultado"]["filas"]
        assert [f["nombre"] for f in filas] == [
            "Caso base",
            "Prueba compuesto",
            "Prueba capacidad",
        ]
        assert filas[0]["escenario_id"] is None
        assert filas[0]["cambio_asignacion"] == 0
        assert filas[0]["z_exacto"] == pytest.approx(64_691_000)
        assert filas[1]["escenario_id"] == escenario_alto
        assert filas[1]["z_exacto"] > filas[0]["z_exacto"]
        assert filas[2]["cambio_asignacion"] >= 0
        assert all(f["z_ag"] >= f["z_exacto"] - 1 for f in filas)
    finally:
        with motor_pruebas.begin() as conexion:
            conexion.execute(
                text("DELETE FROM escenario WHERE nombre LIKE 'Prueba %'")
            )


def test_reporte_de_comparacion_en_pdf(cliente: TestClient) -> None:
    creado = cliente.post(
        "/api/v1/analisis/comparacion", json={"corridas": 2, "parametros_ag": AG_RAPIDO}
    ).json()

    pdf = cliente.get(f"/api/v1/reportes/analisis/{creado['id']}.pdf")
    excel = cliente.get(f"/api/v1/reportes/analisis/{creado['id']}.xlsx")

    assert pdf.content.startswith(b"%PDF")
    libro = load_workbook(io.BytesIO(excel.content))
    assert {"Corridas AG", "Escenarios"} <= set(libro.sheetnames)
