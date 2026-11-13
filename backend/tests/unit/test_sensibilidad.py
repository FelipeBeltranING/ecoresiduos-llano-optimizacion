import numpy as np
import pytest

from app.optimizacion.sensibilidad.analizador import (
    CAPACIDAD,
    CERRAR_RUTA,
    COSTO_TRANSPORTE,
    OFERTA,
    Ajuste,
    aplicar_ajustes,
    balancear,
    calcular_rangos,
    resolver_lp,
)
from tests.utilidades import PENALIZACION_FICTICIA, Z_OPTIMO_CASO_BASE, construir_red_caso_base


def test_lp_rapido_coincide_con_el_optimo_de_referencia() -> None:
    solucion = resolver_lp(construir_red_caso_base())

    assert solucion.costo == pytest.approx(Z_OPTIMO_CASO_BASE)
    assert solucion.duales_capacidad == pytest.approx([-17750, -14250, 0, 0])


def test_combustible_solo_escala_el_transporte() -> None:
    red = construir_red_caso_base()

    nueva = aplicar_ajustes(red, [Ajuste(COSTO_TRANSPORTE, 10)])

    assert nueva.costos[0, 0] == pytest.approx(350 * 110 * 1.1 + 45000)
    assert red.costos[0, 0] == pytest.approx(350 * 110 + 45000)


def test_oferta_y_capacidad_por_objetivo() -> None:
    red = construir_red_caso_base()

    nueva = aplicar_ajustes(red, [Ajuste(OFERTA, 50, "E01"), Ajuste(CAPACIDAD, -50, "P02")])

    assert nueva.oferta[0] == 180
    assert nueva.capacidad[1] == 90


def test_cerrar_ruta_la_deshabilita() -> None:
    nueva = aplicar_ajustes(construir_red_caso_base(), [Ajuste(CERRAR_RUTA, 0, "E05->P01")])

    assert not nueva.rutas_habilitadas[4, 0]


def test_oferta_mayor_que_capacidad_agrega_ficticia() -> None:
    red = aplicar_ajustes(construir_red_caso_base(), [Ajuste(OFERTA, 10)])

    balanceada = balancear(red, PENALIZACION_FICTICIA)

    assert balanceada.tiene_planta_ficticia()
    assert resolver_lp(balanceada) is not None


def test_rangos_contienen_el_valor_actual() -> None:
    red = construir_red_caso_base()

    rangos = calcular_rangos(red)

    for rango in list(rangos.capacidades.values()) + list(rangos.costos.values()):
        assert rango.inferior is None or rango.inferior <= rango.valor + 1e-6
        assert rango.superior is None or rango.superior >= rango.valor - 1e-6
    flujos = resolver_lp(red).flujos
    i, j = np.argwhere(flujos < 1e-9)[0]
    assert rangos.costos[(i, j)].superior is None
