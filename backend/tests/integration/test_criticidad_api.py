from fastapi.testclient import TestClient


def test_criticidad_del_caso_base(cliente_pruebas: TestClient) -> None:
    cliente_pruebas.post("/api/v1/datos/caso-base")
    respuesta = cliente_pruebas.get("/api/v1/criticidad")

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert [n["codigo"] for n in datos["nodos"]] == ["P01", "P03", "P02", "P04"]
    assert datos["nodos"][0]["toneladas_sin_planta"] == 240
    assert round(datos["spearman"], 2) == 0.8
    assert "CICI 2026" in datos["referencia"]


def test_pesos_que_no_suman_uno(cliente_pruebas: TestClient) -> None:
    respuesta = cliente_pruebas.get("/api/v1/criticidad?alfa=0.5&beta=0.5&gamma=0.5")
    assert respuesta.status_code == 422
