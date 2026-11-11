from sqlalchemy import text
from sqlalchemy.orm import Session

TABLAS_V3 = {"escenario", "analisis"}


# Tablas de la migración V3 con RLS activado
def test_tablas_v3_con_rls(sesion_pruebas: Session) -> None:
    consulta = text(
        "SELECT relname, relrowsecurity FROM pg_class "
        "WHERE relkind = 'r' AND relname = ANY(:tablas)"
    )
    encontradas = set()
    for fila in sesion_pruebas.execute(consulta, {"tablas": list(TABLAS_V3)}):
        encontradas.add(fila.relname)
        assert fila.relrowsecurity is True, fila.relname

    assert encontradas == TABLAS_V3
