import numpy as np
import pytest

from app.optimizacion.contratos import ParametrosAG, ejecutar_genetico
from tests.utilidades import Z_OPTIMO_CASO_BASE, construir_red_caso_base

PENDIENTE = pytest.mark.skip(reason="pendiente: AG HU-09")
TOLERANCIA = 1e-6


@PENDIENTE
def test_misma_semilla_mismo_resultado() -> None:
    red = construir_red_caso_base()
    parametros = ParametrosAG(semilla=42)

    primera = ejecutar_genetico(red, parametros)
    segunda = ejecutar_genetico(red, parametros)

    assert primera.costo_total == segunda.costo_total
    assert np.array_equal(primera.flujos, segunda.flujos)


@PENDIENTE
def test_cada_fila_cumple_la_oferta() -> None:
    red = construir_red_caso_base()

    resultado = ejecutar_genetico(red, ParametrosAG(semilla=42))

    oferta_enviada = resultado.flujos.sum(axis=1)
    for i in range(red.numero_empresas()):
        assert abs(oferta_enviada[i] - red.oferta[i]) <= TOLERANCIA


@PENDIENTE
def test_gap_promedio_en_diez_corridas() -> None:
    red = construir_red_caso_base()

    gaps = []
    for semilla in range(10):
        resultado = ejecutar_genetico(red, ParametrosAG(semilla=semilla))
        gap = (resultado.costo_total - Z_OPTIMO_CASO_BASE) / Z_OPTIMO_CASO_BASE * 100
        gaps.append(gap)

    assert sum(gaps) / len(gaps) <= 2


@PENDIENTE
def test_mejor_costo_nunca_sube_con_elitismo() -> None:
    red = construir_red_caso_base()

    resultado = ejecutar_genetico(red, ParametrosAG(semilla=42, elitismo=2))

    assert len(resultado.convergencia) > 0
    for anterior, actual in zip(resultado.convergencia, resultado.convergencia[1:], strict=False):
        assert actual.mejor_costo <= anterior.mejor_costo + TOLERANCIA
