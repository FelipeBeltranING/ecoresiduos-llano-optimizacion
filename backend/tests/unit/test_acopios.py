"""Centros de acopio como nodos de paso: flujo de costo mínimo por arcos (HU-17)."""

import numpy as np
import pytest

from app.optimizacion.contratos import ParametrosAG, ejecutar_genetico, resolver_exacto
from app.optimizacion.red import ValidadorRed, preparar_red_para_motor
from app.optimizacion.sensibilidad.analizador import (
    CAPACIDAD,
    Ajuste,
    aplicar_ajustes,
    balancear,
    resolver_lp,
)
from app.optimizacion.verificador import verificar_solucion
from app.services.ejecucion_service import red_desde_snapshot, snapshot_de_red
from tests.utilidades import (
    PENALIZACION_FICTICIA,
    TONELADAS_POR_ACOPIO,
    Z_OPTIMO_CASO_BASE,
    Z_OPTIMO_CON_ACOPIOS,
    construir_red_caso_base,
)


def red_lista(**opciones):
    red = construir_red_caso_base(**opciones)
    validacion = ValidadorRed(PENALIZACION_FICTICIA).validar(red)
    return preparar_red_para_motor(red, validacion)


@pytest.fixture(scope="module")
def red_con_acopios():
    return red_lista(con_acopios=True)


@pytest.fixture(scope="module")
def exacto_con_acopios(red_con_acopios):
    return resolver_exacto(red_con_acopios)


def test_abrir_acopios_baja_el_costo(exacto_con_acopios) -> None:
    assert exacto_con_acopios.estado == "Óptimo"
    assert exacto_con_acopios.costo_total == pytest.approx(Z_OPTIMO_CON_ACOPIOS, abs=1)
    assert exacto_con_acopios.costo_total < Z_OPTIMO_CASO_BASE


def test_toneladas_que_pasan_por_cada_acopio(exacto_con_acopios) -> None:
    entra = exacto_con_acopios.flujos_a_acopio.sum(axis=0)
    assert entra == pytest.approx(TONELADAS_POR_ACOPIO, abs=1e-6)


def test_solucion_conserva_el_flujo_y_respeta_capacidades(
    red_con_acopios, exacto_con_acopios
) -> None:
    r = exacto_con_acopios
    entra = r.flujos_a_acopio.sum(axis=0)
    sale = r.flujos_desde_acopio.sum(axis=1)
    assert entra == pytest.approx(sale)
    assert np.all(entra <= red_con_acopios.capacidad_acopios + 1e-6)
    reporte = verificar_solucion(
        red_con_acopios, r.flujos, r.flujos_a_acopio, r.flujos_desde_acopio
    )
    assert reporte.es_factible()


def test_sin_cupo_en_los_acopios_vuelve_al_modelo_de_transporte() -> None:
    resultado = resolver_exacto(red_lista(con_acopios=True, capacidad_acopio=0))
    assert resultado.costo_total == pytest.approx(Z_OPTIMO_CASO_BASE, abs=1)


def test_verificador_detecta_flujo_que_no_sale_del_acopio(
    red_con_acopios, exacto_con_acopios
) -> None:
    r = exacto_con_acopios
    desde = r.flujos_desde_acopio.copy()
    desde[0] = 0.0
    reporte = verificar_solucion(red_con_acopios, r.flujos, r.flujos_a_acopio, desde)
    assert reporte.violacion_conservacion > 0
    assert not reporte.es_factible()


def test_highs_por_caminos_coincide_con_cbc_por_arcos(red_con_acopios) -> None:
    solucion = resolver_lp(red_con_acopios)
    assert solucion.costo == pytest.approx(Z_OPTIMO_CON_ACOPIOS, abs=1)


def test_ag_por_caminos_es_factible_y_cercano_al_optimo(red_con_acopios) -> None:
    resultado = ejecutar_genetico(red_con_acopios, ParametrosAG(semilla=42))
    reporte = verificar_solucion(
        red_con_acopios,
        resultado.flujos,
        resultado.flujos_a_acopio,
        resultado.flujos_desde_acopio,
    )
    gap = (resultado.costo_total - Z_OPTIMO_CON_ACOPIOS) / Z_OPTIMO_CON_ACOPIOS
    assert reporte.es_factible()
    assert 0 <= gap < 0.02


def test_cerrar_un_acopio_es_un_escenario_de_sensibilidad() -> None:
    red = construir_red_caso_base(con_acopios=True)
    cerrado = aplicar_ajustes(red, [Ajuste(CAPACIDAD, -100, "A01")])
    costo = resolver_lp(balancear(cerrado, PENALIZACION_FICTICIA)).costo
    assert cerrado.capacidad_acopios[0] == 0
    assert red.capacidad_acopios[0] == 200
    assert Z_OPTIMO_CON_ACOPIOS < costo <= Z_OPTIMO_CASO_BASE


def test_snapshot_conserva_los_acopios(red_con_acopios) -> None:
    copia = red_desde_snapshot(snapshot_de_red(red_con_acopios))
    assert copia.codigos_acopios == ["A01", "A02"]
    assert resolver_exacto(copia).costo_total == pytest.approx(Z_OPTIMO_CON_ACOPIOS, abs=1)
