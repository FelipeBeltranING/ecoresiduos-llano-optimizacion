from app.optimizacion.contratos import ParametrosAG, ejecutar_genetico, resolver_exacto
from tests.utilidades import construir_red_caso_base


def test_resolver_exacto_conectado() -> None:
    resultado = resolver_exacto(construir_red_caso_base())

    assert resultado.flujos.shape == (10, 4)
    assert resultado.tiempo_ms > 0


def test_ejecutar_genetico_conectado() -> None:
    resultado = ejecutar_genetico(construir_red_caso_base(), ParametrosAG(semilla=1))

    assert resultado.flujos.shape == (10, 4)
    assert len(resultado.convergencia) > 0


def test_parametros_ag_por_defecto() -> None:
    parametros = ParametrosAG()

    assert parametros.tamano_poblacion == 100
    assert parametros.elitismo == 2
    assert parametros.lambda_pen == 1_000_000
