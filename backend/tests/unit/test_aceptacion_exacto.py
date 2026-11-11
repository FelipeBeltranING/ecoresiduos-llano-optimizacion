import numpy as np
import pytest

from app.optimizacion.contratos import ESTADO_OPTIMO, resolver_exacto
from app.optimizacion.red import CODIGO_PLANTA_FICTICIA, ValidadorRed, preparar_red_para_motor
from tests.utilidades import PENALIZACION_FICTICIA, Z_OPTIMO_CASO_BASE, construir_red_caso_base

PENDIENTE = pytest.mark.skip(reason="pendiente: modelo exacto HU-07")
TOLERANCIA = 1e-6


# Resolución del caso base con la red preparada para el motor
def resolver_caso_base(factor_oferta: float = 1.0):
    red = construir_red_caso_base(factor_oferta)
    validacion = ValidadorRed(PENALIZACION_FICTICIA).validar(red)
    red_motor = preparar_red_para_motor(red, validacion)
    return red_motor, resolver_exacto(red_motor)


@PENDIENTE
def test_estado_optimo_y_costo_del_caso_base() -> None:
    _, resultado = resolver_caso_base()

    assert resultado.estado == ESTADO_OPTIMO
    assert resultado.costo_total == pytest.approx(Z_OPTIMO_CASO_BASE)


@PENDIENTE
def test_once_rutas_con_flujo() -> None:
    _, resultado = resolver_caso_base()

    rutas_con_flujo = np.sum(resultado.flujos > TOLERANCIA)
    assert rutas_con_flujo == 11


@PENDIENTE
def test_duales_de_capacidad() -> None:
    _, resultado = resolver_caso_base()

    assert resultado.duales_capacidad == pytest.approx([-17750, -14250, 0, 0])


@PENDIENTE
def test_holguras_de_capacidad() -> None:
    _, resultado = resolver_caso_base()

    assert resultado.holguras == pytest.approx([0, 0, 5, 55], abs=TOLERANCIA)


@PENDIENTE
def test_cero_violaciones() -> None:
    red, resultado = resolver_caso_base()

    oferta_enviada = resultado.flujos.sum(axis=1)
    capacidad_usada = resultado.flujos.sum(axis=0)

    for i in range(red.numero_empresas()):
        assert abs(oferta_enviada[i] - red.oferta[i]) <= TOLERANCIA
    for j in range(red.numero_plantas()):
        assert capacidad_usada[j] <= red.capacidad[j] + TOLERANCIA
    assert resultado.flujos.min() >= -TOLERANCIA


@PENDIENTE
def test_oferta_mas_diez_por_ciento_usa_planta_ficticia() -> None:
    red, resultado = resolver_caso_base(factor_oferta=1.1)

    columna_ficticia = red.codigos_plantas.index(CODIGO_PLANTA_FICTICIA)
    toneladas_ficticia = resultado.flujos[:, columna_ficticia].sum()
    assert toneladas_ficticia == pytest.approx(29)
