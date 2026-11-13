from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_health_responde_200() -> None:
    respuesta = cliente.get("/api/v1/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}
