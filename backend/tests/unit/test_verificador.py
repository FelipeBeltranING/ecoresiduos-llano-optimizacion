import numpy as np

from app.optimizacion.contratos import resolver_exacto
from app.optimizacion.verificador import verificar_solucion
from tests.utilidades import construir_red_caso_base


def test_solucion_exacta_es_factible() -> None:
    red = construir_red_caso_base()
    resultado = resolver_exacto(red)

    reporte = verificar_solucion(red, resultado.flujos)

    assert reporte.es_factible()
    assert reporte.detalles == []


def test_detecta_exceso_de_capacidad() -> None:
    red = construir_red_caso_base()
    flujos = np.zeros((red.numero_empresas(), red.numero_plantas()))
    flujos[:, 0] = red.oferta

    reporte = verificar_solucion(red, flujos)

    assert not reporte.es_factible()
    assert reporte.violacion_capacidad == red.oferta.sum() - red.capacidad[0]
    assert any("P01" in detalle for detalle in reporte.detalles)
