import pytest

from app.optimizacion.contratos import ParametrosAG, ejecutar_genetico, resolver_exacto
from tests.utilidades import construir_red_caso_base


# El contrato del exacto devuelve el resultado completo del modelo
def test_resolver_exacto_conectado() -> None:
    resultado = resolver_exacto(construir_red_caso_base())

    assert resultado.flujos.shape == (10, 4)
    assert resultado.tiempo_ms > 0


def test_ejecutar_genetico_pendiente() -> None:
    with pytest.raises(NotImplementedError, match="HU-09"):
        ejecutar_genetico(construir_red_caso_base(), ParametrosAG())


# Valores por defecto de los parámetros del AG (README, sección 6)
def test_parametros_ag_por_defecto() -> None:
    parametros = ParametrosAG()

    assert parametros.tamano_poblacion == 100
    assert parametros.elitismo == 2
    assert parametros.lambda_pen == 1_000_000
