"""Transbordo manual: caso pequeño con valores calculados a mano (HU-17)."""

import numpy as np
import pytest

from app.optimizacion.contratos import ESTADO_OPTIMO, resolver_exacto
from app.optimizacion.red import (
    DatosAcopio,
    DatosEmpresa,
    DatosPlanta,
    DatosRuta,
    RedLogistica,
    ValidadorRed,
    construir_red,
    preparar_red_para_motor,
)
from tests.utilidades import PENALIZACION_FICTICIA


# Dos empresas, dos plantas y un acopio de capacidad 10.
# Directo cuesta 100 COP/t; por el acopio cuesta 10 + 10 = 20 COP/t.
def red_transbordo() -> RedLogistica:
    empresas = [DatosEmpresa("E1", 10), DatosEmpresa("E2", 10)]
    plantas = [DatosPlanta("P1", 10, 0), DatosPlanta("P2", 10, 0)]
    acopios = [DatosAcopio("A1", 10, 0)]
    rutas = [
        DatosRuta("E1", "P1", 100, None, True),
        DatosRuta("E2", "P2", 100, None, True),
        DatosRuta("E1", "A1", 10, None, True),
        DatosRuta("E2", "A1", 10, None, True),
        DatosRuta("A1", "P1", 10, None, True),
        DatosRuta("A1", "P2", 10, None, True),
    ]
    red = construir_red(empresas, plantas, rutas, 1, acopios)
    validacion = ValidadorRed(PENALIZACION_FICTICIA).validar(red)
    return preparar_red_para_motor(red, validacion)


def test_costo_y_flujo_por_el_acopio() -> None:
    resultado = resolver_exacto(red_transbordo())

    # 10 t por el acopio a 20 COP/t + 10 t directas a 100 COP/t
    assert resultado.estado == ESTADO_OPTIMO
    assert resultado.costo_total == pytest.approx(1_200)
    assert resultado.flujos_a_acopio.sum(axis=0) == pytest.approx([10])
    assert resultado.flujos_desde_acopio.sum(axis=1) == pytest.approx([10])
    assert resultado.holguras_acopio == pytest.approx([0])


def test_dual_del_acopio_saturado() -> None:
    resultado = resolver_exacto(red_transbordo())

    # Una tonelada más de capacidad permite sustituir 100 por 20 COP/t
    assert resultado.duales_acopio == pytest.approx([-80])


def test_planta_y_conservacion_del_acopio() -> None:
    red = red_transbordo()
    resultado = resolver_exacto(red)

    entra = resultado.flujos_a_acopio.sum(axis=0)
    sale = resultado.flujos_desde_acopio.sum(axis=1)
    assert entra == pytest.approx(sale)
    assert resultado.flujos.sum(axis=0) + resultado.flujos_desde_acopio.sum(axis=0) == (
        pytest.approx(red.capacidad)
    )
    assert np.all(resultado.flujos >= 0)
