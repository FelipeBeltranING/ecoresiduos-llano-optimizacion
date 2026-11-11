import numpy as np
import pytest

from app.optimizacion.contratos import ParametrosAG, ejecutar_genetico
from tests.utilidades import Z_OPTIMO_CASO_BASE, construir_red_caso_base

TOLERANCIA = 1e-6


def test_misma_semilla_mismo_resultado() -> None:
    red = construir_red_caso_base()
    parametros = ParametrosAG(semilla=42)

    primera = ejecutar_genetico(red, parametros)
    segunda = ejecutar_genetico(red, parametros)

    assert primera.costo_total == segunda.costo_total
    assert np.array_equal(primera.flujos, segunda.flujos)


def test_cada_fila_cumple_la_oferta() -> None:
    red = construir_red_caso_base()

    resultado = ejecutar_genetico(red, ParametrosAG(semilla=42))

    oferta_enviada = resultado.flujos.sum(axis=1)
    for i in range(red.numero_empresas()):
        assert abs(oferta_enviada[i] - red.oferta[i]) <= TOLERANCIA


def test_gap_promedio_en_diez_corridas() -> None:
    red = construir_red_caso_base()

    gaps = []
    for semilla in range(10):
        resultado = ejecutar_genetico(red, ParametrosAG(semilla=semilla))
        gap = (resultado.costo_total - Z_OPTIMO_CASO_BASE) / Z_OPTIMO_CASO_BASE * 100
        gaps.append(gap)

    assert sum(gaps) / len(gaps) <= 2


def test_mejor_costo_nunca_sube_con_elitismo() -> None:
    red = construir_red_caso_base()

    resultado = ejecutar_genetico(red, ParametrosAG(semilla=42, elitismo=2))

    assert len(resultado.convergencia) > 0
    for anterior, actual in zip(resultado.convergencia, resultado.convergencia[1:], strict=False):
        assert actual.mejor_costo <= anterior.mejor_costo + TOLERANCIA


def test_cruce_de_dos_puntos_y_ruleta_cumplen_restricciones() -> None:
    red = construir_red_caso_base()
    parametros = ParametrosAG(semilla=3, tipo_cruce="dos_puntos", tipo_seleccion="ruleta")

    resultado = ejecutar_genetico(red, parametros)

    assert resultado.violaciones <= TOLERANCIA
    assert resultado.flujos.sum(axis=0) == pytest.approx(
        np.minimum(resultado.flujos.sum(axis=0), red.capacidad)
    )


def test_no_envia_flujo_por_rutas_cerradas() -> None:
    red = construir_red_caso_base()
    red.rutas_habilitadas[0, 0] = False

    resultado = ejecutar_genetico(red, ParametrosAG(semilla=1))

    assert resultado.flujos[0, 0] == 0
