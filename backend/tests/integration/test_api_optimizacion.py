import uuid

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.optimizacion import contratos
from app.optimizacion.contratos import (
    ESTADO_OPTIMO,
    ParametrosAG,
    RegistroConvergencia,
    ResultadoExacto,
    ResultadoGenetico,
)
from app.optimizacion.red import RedLogistica


@pytest.fixture
def cliente_con_caso_base(cliente_pruebas: TestClient) -> TestClient:
    cliente_pruebas.post("/api/v1/datos/caso-base")
    return cliente_pruebas


def contar_ejecuciones(sesion: Session) -> int:
    return sesion.execute(text("SELECT count(*) FROM ejecucion")).scalar_one()


def flujos_de_prueba(red: RedLogistica) -> np.ndarray:
    flujos = np.zeros(red.costos.shape)
    for i in range(red.numero_empresas()):
        flujos[i, 0] = red.oferta[i]
    return flujos


def exacto_falso(red: RedLogistica) -> ResultadoExacto:
    m = red.numero_empresas()
    n = red.numero_plantas()
    return ResultadoExacto(
        estado=ESTADO_OPTIMO,
        costo_total=123.0,
        flujos=flujos_de_prueba(red),
        duales_oferta=np.ones(m),
        duales_capacidad=np.zeros(n),
        costos_reducidos=np.zeros((m, n)),
        holguras=np.zeros(n),
        tiempo_ms=5.0,
    )


def genetico_falso(red: RedLogistica, parametros: ParametrosAG) -> ResultadoGenetico:
    convergencia = []
    for generacion in range(3):
        convergencia.append(
            RegistroConvergencia(
                generacion=generacion, mejor_costo=100 - generacion, costo_promedio=150
            )
        )
    return ResultadoGenetico(
        costo_total=97.0,
        flujos=flujos_de_prueba(red),
        violaciones=0.0,
        convergencia=convergencia,
        tiempo_ms=8.0,
    )


def test_validacion_de_la_red(cliente_con_caso_base: TestClient) -> None:
    respuesta = cliente_con_caso_base.get("/api/v1/red/validacion")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["es_valida"] is True
    assert cuerpo["holgura_capacidad"] == 60
    assert cuerpo["necesita_planta_ficticia"] is False


def test_exacto_real_resuelve_el_caso_base(
    cliente_con_caso_base: TestClient, sesion_pruebas: Session
) -> None:
    antes = contar_ejecuciones(sesion_pruebas)

    respuesta = cliente_con_caso_base.post("/api/v1/optimizacion/exacto")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == ESTADO_OPTIMO
    assert cuerpo["costo_total"] == 64_691_000
    assert contar_ejecuciones(sesion_pruebas) == antes + 1


def test_genetico_real_guarda_convergencia(
    cliente_con_caso_base: TestClient, sesion_pruebas: Session
) -> None:
    antes = contar_ejecuciones(sesion_pruebas)

    respuesta = cliente_con_caso_base.post(
        "/api/v1/optimizacion/genetico", json={"semilla": 42, "generaciones": 30}
    )

    assert respuesta.status_code == 201
    ejecucion_id = respuesta.json()["id"]
    detalle = cliente_con_caso_base.get(f"/api/v1/ejecuciones/{ejecucion_id}").json()
    assert len(detalle["convergencia"]) > 0
    assert contar_ejecuciones(sesion_pruebas) == antes + 1


def test_ejecucion_inexistente_da_404(cliente_pruebas: TestClient) -> None:
    respuesta = cliente_pruebas.get(f"/api/v1/ejecuciones/{uuid.uuid4()}")

    assert respuesta.status_code == 404


def test_guarda_resultado_del_exacto(
    cliente_con_caso_base: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(contratos, "resolver_exacto", exacto_falso)

    creada = cliente_con_caso_base.post("/api/v1/optimizacion/exacto")
    assert creada.status_code == 201
    ejecucion_id = creada.json()["id"]

    detalle = cliente_con_caso_base.get(f"/api/v1/ejecuciones/{ejecucion_id}").json()

    assert detalle["metodo"] == "EXACTO"
    assert detalle["estado"] == ESTADO_OPTIMO
    assert detalle["costo_total"] == 123
    assert len(detalle["flujos"]) == 10
    assert detalle["flujos"][0]["destino"] == "P01"
    tipos = {}
    for registro in detalle["sensibilidad"]:
        tipos[registro["tipo"]] = tipos.get(registro["tipo"], 0) + 1
    assert tipos == {
        "DUAL_OFERTA": 10,
        "DUAL_CAPACIDAD": 4,
        "HOLGURA_CAPACIDAD": 4,
        "COSTO_REDUCIDO": 40,
    }


def test_guarda_resultado_del_genetico(
    cliente_con_caso_base: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(contratos, "ejecutar_genetico", genetico_falso)

    creada = cliente_con_caso_base.post("/api/v1/optimizacion/genetico", json={"semilla": 7})
    assert creada.status_code == 201
    ejecucion_id = creada.json()["id"]

    detalle = cliente_con_caso_base.get(f"/api/v1/ejecuciones/{ejecucion_id}").json()

    assert detalle["metodo"] == "GENETICO"
    assert detalle["parametros"]["semilla"] == 7
    assert detalle["parametros"]["lambda_pen"] == 1_000_000
    assert len(detalle["convergencia"]) == 3
    assert detalle["convergencia"][2]["mejor_costo"] == 98
