from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)
URL_GENETICO = "/api/v1/optimizacion/genetico"


# La API rechaza parámetros del AG inválidos antes de tocar la base de datos
def test_prob_cruce_fuera_de_rango_da_422() -> None:
    respuesta = cliente.post(URL_GENETICO, json={"prob_cruce": 1.5})

    assert respuesta.status_code == 422


def test_poblacion_menor_que_10_da_422() -> None:
    respuesta = cliente.post(URL_GENETICO, json={"tamano_poblacion": 5})

    assert respuesta.status_code == 422


def test_elitismo_mayor_que_poblacion_da_422() -> None:
    respuesta = cliente.post(URL_GENETICO, json={"tamano_poblacion": 10, "elitismo": 10})

    assert respuesta.status_code == 422
