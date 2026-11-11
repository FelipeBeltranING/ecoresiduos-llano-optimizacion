import io
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook, load_workbook
from sqlalchemy import text
from sqlalchemy.engine import Engine

EMPRESA_PRUEBA = {
    "codigo": "TST01",
    "tipo": "FUENTE",
    "nombre": "Empresa de prueba",
    "municipio": "Puerto López",
    "tipo_residuo": "Arroz (cascarilla)",
    "oferta_t": 10,
    "latitud": 4.08,
    "longitud": -72.95,
}


# Caso base cargado y limpieza de los nodos de prueba al terminar
@pytest.fixture
def cliente(cliente_pruebas: TestClient, motor_pruebas: Engine) -> Iterator[TestClient]:
    cliente_pruebas.post("/api/v1/datos/caso-base")
    yield cliente_pruebas
    with motor_pruebas.begin() as conexion:
        conexion.execute(
            text(
                "DELETE FROM flujo_resultado WHERE origen_id IN "
                "(SELECT id FROM nodo WHERE codigo LIKE 'TST%')"
            )
        )
        conexion.execute(text("DELETE FROM nodo WHERE codigo LIKE 'TST%'"))
        conexion.execute(text("UPDATE parametro_global SET valor = 350 WHERE clave = 'costo_km_t'"))
        conexion.execute(text("UPDATE ruta SET habilitada = true, costo_km_t = NULL"))


def test_crear_empresa_genera_sus_rutas(cliente: TestClient) -> None:
    respuesta = cliente.post("/api/v1/nodos", json=EMPRESA_PRUEBA)

    assert respuesta.status_code == 201
    matriz = cliente.get("/api/v1/rutas/matriz").json()
    rutas_nuevas = [r for r in matriz["rutas"] if r["origen"] == "TST01"]
    assert len(rutas_nuevas) == 4
    assert all(r["distancia_km"] > 0 for r in rutas_nuevas)


def test_codigo_repetido_da_409(cliente: TestClient) -> None:
    cliente.post("/api/v1/nodos", json=EMPRESA_PRUEBA)

    respuesta = cliente.post("/api/v1/nodos", json=EMPRESA_PRUEBA)

    assert respuesta.status_code == 409


def test_empresa_sin_oferta_da_422(cliente: TestClient) -> None:
    datos = dict(EMPRESA_PRUEBA)
    datos.pop("oferta_t")

    respuesta = cliente.post("/api/v1/nodos", json=datos)

    assert respuesta.status_code == 422


def test_desactivar_saca_el_nodo_de_la_red(cliente: TestClient) -> None:
    cliente.post("/api/v1/nodos", json=EMPRESA_PRUEBA)
    oferta_con = cliente.get("/api/v1/red/validacion").json()["oferta_total"]

    respuesta = cliente.delete("/api/v1/nodos/TST01")

    assert respuesta.json()["activo"] is False
    oferta_sin = cliente.get("/api/v1/red/validacion").json()["oferta_total"]
    assert oferta_con - oferta_sin == 10


def test_editar_planta_y_listar_por_tipo(cliente: TestClient) -> None:
    plantas = cliente.get("/api/v1/nodos", params={"tipo": "PLANTA"}).json()

    assert len([p for p in plantas if p["codigo"].startswith("P0")]) == 4
    respuesta = cliente.patch("/api/v1/nodos/P01", json={"costo_operacion_t": 45000})
    assert respuesta.status_code == 200


def test_actualizar_rutas_por_lote_cambia_el_costo(cliente: TestClient) -> None:
    cambios = [
        {"origen": "E01", "destino": "P01", "costo_km_t": 500},
        {"origen": "E01", "destino": "P04", "habilitada": False},
    ]

    respuesta = cliente.put("/api/v1/rutas", json=cambios)

    assert respuesta.json() == {"actualizadas": 2, "creadas": 0}
    matriz = cliente.get("/api/v1/rutas/matriz").json()
    ruta = next(r for r in matriz["rutas"] if r["origen"] == "E01" and r["destino"] == "P01")
    assert ruta["costo_unitario"] == 500 * 110 + 45000
    cerrada = next(r for r in matriz["rutas"] if r["origen"] == "E01" and r["destino"] == "P04")
    assert cerrada["habilitada"] is False


def test_parametro_costo_km(cliente: TestClient) -> None:
    respuesta = cliente.put("/api/v1/parametros/costo_km_t", json={"valor": 400})

    assert respuesta.json()["valor"] == 400
    claves = {p["clave"] for p in cliente.get("/api/v1/parametros").json()}
    assert {"costo_km_t", "penalizacion_ficticia", "lambda_ag"} <= claves


def test_exportar_e_importar_ida_y_vuelta(cliente: TestClient) -> None:
    exportado = cliente.get("/api/v1/datos/exportar")
    assert exportado.status_code == 200
    libro = load_workbook(io.BytesIO(exportado.content))
    assert {"Empresas", "Plantas", "Rutas", "Parametros"} <= set(libro.sheetnames)

    respuesta = cliente.post(
        "/api/v1/datos/importar",
        files={"archivo": ("red.xlsx", exportado.content, "application/octet-stream")},
    )

    cuerpo = respuesta.json()
    assert cuerpo["importado"] is True
    assert cuerpo["empresas"] >= 10
    assert cuerpo["errores"] == []


def test_importar_con_errores_no_guarda_nada(cliente: TestClient) -> None:
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Empresas"
    hoja.append(["codigo", "nombre", "municipio", "oferta_t", "latitud", "longitud"])
    hoja.append(["TST02", "Buena", "Acacías", 5, 3.98, -73.76])
    hoja.append(["TST03", "Sin oferta", "Acacías", None, 3.98, -73.76])
    salida = io.BytesIO()
    libro.save(salida)

    respuesta = cliente.post(
        "/api/v1/datos/importar",
        files={"archivo": ("red.xlsx", salida.getvalue(), "application/octet-stream")},
    )

    cuerpo = respuesta.json()
    assert cuerpo["importado"] is False
    assert cuerpo["errores"][0]["fila"] == 3
    assert cliente.get("/api/v1/nodos/TST02").status_code == 404
