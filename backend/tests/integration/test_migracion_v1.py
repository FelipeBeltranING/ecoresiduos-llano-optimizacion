from sqlalchemy import text
from sqlalchemy.orm import Session


def test_existen_las_tablas_de_la_red(sesion_pruebas: Session) -> None:
    consulta = text(
        "SELECT tablename FROM pg_tables "
        "WHERE schemaname = 'public' AND tablename IN ('nodo', 'ruta', 'parametro_global')"
    )
    tablas = set()
    for fila in sesion_pruebas.execute(consulta):
        tablas.add(fila.tablename)

    assert tablas == {"nodo", "ruta", "parametro_global"}


def test_rls_activado(sesion_pruebas: Session) -> None:
    consulta = text(
        "SELECT relname, relrowsecurity FROM pg_class "
        "WHERE relname IN ('nodo', 'ruta', 'parametro_global')"
    )
    for fila in sesion_pruebas.execute(consulta):
        assert fila.relrowsecurity is True, fila.relname


def test_parametros_semilla(sesion_pruebas: Session) -> None:
    consulta = text("SELECT clave, valor FROM parametro_global")
    parametros = {}
    for fila in sesion_pruebas.execute(consulta):
        parametros[fila.clave] = float(fila.valor)

    assert parametros == {
        "costo_km_t": 350,
        "tarifa_recepcion_t": 0,
        "penalizacion_ficticia": 1000000,
        "lambda_ag": 1000000,
    }
