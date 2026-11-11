from sqlalchemy import text
from sqlalchemy.orm import Session

TABLAS_V2 = {"ejecucion", "flujo_resultado", "sensibilidad_resultado", "convergencia_ag"}


# Tablas de la migración V2 con RLS activado
def test_tablas_v2_con_rls(sesion_pruebas: Session) -> None:
    consulta = text(
        "SELECT relname, relrowsecurity FROM pg_class "
        "WHERE relkind = 'r' AND relname = ANY(:tablas)"
    )
    encontradas = set()
    for fila in sesion_pruebas.execute(consulta, {"tablas": list(TABLAS_V2)}):
        encontradas.add(fila.relname)
        assert fila.relrowsecurity is True, fila.relname

    assert encontradas == TABLAS_V2
