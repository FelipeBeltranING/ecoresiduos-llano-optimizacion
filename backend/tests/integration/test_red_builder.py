from sqlalchemy.orm import Session

from app.services.caso_base_service import cargar_caso_base
from app.services.red_builder import RedBuilder


# La red armada desde la base coincide con el caso base
def test_red_builder_con_caso_base(sesion_pruebas: Session) -> None:
    cargar_caso_base(sesion_pruebas)
    constructor = RedBuilder(sesion_pruebas)

    red = constructor.construir()
    validacion = constructor.crear_validador().validar(red)

    assert red.codigos_empresas[0] == "E01"
    assert red.codigos_plantas == ["P01", "P02", "P03", "P04"]
    assert red.costos.shape == (10, 4)
    assert red.costo("E04", "P04") == 104_750
    assert validacion.oferta_total == 890
    assert validacion.capacidad_total == 950
    assert validacion.holgura_capacidad == 60
    assert validacion.necesita_planta_ficticia is False
