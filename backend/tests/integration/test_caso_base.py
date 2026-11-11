from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


# Conteo de nodos y rutas en la base
def contar(sesion: Session, consulta: str) -> int:
    return sesion.execute(text(consulta)).scalar_one()


# Carga del caso base: 10 empresas, 4 plantas y 40 rutas
def test_carga_el_caso_base(cliente_pruebas: TestClient, sesion_pruebas: Session) -> None:
    respuesta = cliente_pruebas.post("/api/v1/datos/caso-base")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"empresas": 10, "plantas": 4, "rutas": 40}
    assert contar(sesion_pruebas, "SELECT count(*) FROM nodo WHERE tipo = 'FUENTE'") == 10
    assert contar(sesion_pruebas, "SELECT count(*) FROM nodo WHERE tipo = 'PLANTA'") == 4
    assert contar(sesion_pruebas, "SELECT count(*) FROM ruta") == 40


# Cargarlo dos veces no duplica registros
def test_cargar_dos_veces_no_duplica(
    cliente_pruebas: TestClient, sesion_pruebas: Session
) -> None:
    cliente_pruebas.post("/api/v1/datos/caso-base")
    respuesta = cliente_pruebas.post("/api/v1/datos/caso-base")

    assert respuesta.status_code == 200
    assert contar(sesion_pruebas, "SELECT count(*) FROM nodo") == 14
    assert contar(sesion_pruebas, "SELECT count(*) FROM ruta") == 40


# Los valores quedan como en el caso base aunque se hayan modificado antes
def test_recarga_restaura_valores(cliente_pruebas: TestClient, sesion_pruebas: Session) -> None:
    cliente_pruebas.post("/api/v1/datos/caso-base")
    sesion_pruebas.execute(text("UPDATE nodo SET oferta_t = 1 WHERE codigo = 'E04'"))
    sesion_pruebas.commit()

    cliente_pruebas.post("/api/v1/datos/caso-base")

    oferta = sesion_pruebas.execute(
        text("SELECT oferta_t FROM nodo WHERE codigo = 'E04'")
    ).scalar_one()
    assert float(oferta) == 140
