import pytest

from app.optimizacion.red import (
    CODIGO_PLANTA_FICTICIA,
    DatosEmpresa,
    DatosPlanta,
    DatosRuta,
    ValidadorRed,
    construir_red,
    preparar_red_para_motor,
)
from tests.utilidades import PENALIZACION_FICTICIA, construir_red_caso_base

validador = ValidadorRed(penalizacion_ficticia=PENALIZACION_FICTICIA)


def test_red_caso_base_tiene_10_empresas_y_4_plantas() -> None:
    red = construir_red_caso_base()

    assert red.numero_empresas() == 10
    assert red.numero_plantas() == 4
    assert red.costos.shape == (10, 4)
    assert red.rutas_habilitadas.all()


def test_validacion_caso_base() -> None:
    resultado = validador.validar(construir_red_caso_base())

    assert resultado.oferta_total == 890
    assert resultado.capacidad_total == 950
    assert resultado.holgura_capacidad == 60
    assert resultado.necesita_planta_ficticia is False
    assert resultado.capacidad_ficticia == 0
    assert resultado.nodos_aislados == []
    assert resultado.es_valida() is True


def test_costo_e04_p04() -> None:
    red = construir_red_caso_base()

    assert red.costo("E04", "P04") == 104_750


def test_ruta_con_costo_km_propio() -> None:
    empresas = [DatosEmpresa(codigo="E01", oferta=10)]
    plantas = [DatosPlanta(codigo="P01", capacidad=20, costo_operacion=1000)]
    rutas = [
        DatosRuta(origen="E01", destino="P01", distancia_km=10, costo_km_t=500, habilitada=True)
    ]

    red = construir_red(empresas, plantas, rutas, costo_km_global=350)

    assert red.costo("E01", "P01") == 500 * 10 + 1000


def test_oferta_mayor_que_capacidad_pide_planta_ficticia() -> None:
    red = construir_red_caso_base(factor_oferta=1.1)

    resultado = validador.validar(red)

    assert resultado.oferta_total == pytest.approx(979)
    assert resultado.necesita_planta_ficticia is True
    assert resultado.capacidad_ficticia == pytest.approx(29)
    assert resultado.costo_ficticia == PENALIZACION_FICTICIA


def test_preparar_red_agrega_planta_ficticia() -> None:
    red = construir_red_caso_base(factor_oferta=1.1)
    resultado = validador.validar(red)

    red_motor = preparar_red_para_motor(red, resultado)

    assert red_motor.codigos_plantas[-1] == CODIGO_PLANTA_FICTICIA
    assert red_motor.capacidad[-1] == pytest.approx(29)
    assert red_motor.costo("E01", CODIGO_PLANTA_FICTICIA) == PENALIZACION_FICTICIA
    assert red_motor.capacidad.sum() == pytest.approx(red_motor.oferta.sum())


def test_preparar_red_sin_ficticia() -> None:
    red = construir_red_caso_base()
    resultado = validador.validar(red)

    assert preparar_red_para_motor(red, resultado) is red


def test_detecta_nodo_aislado() -> None:
    empresas = [DatosEmpresa(codigo="E01", oferta=10), DatosEmpresa(codigo="E02", oferta=5)]
    plantas = [DatosPlanta(codigo="P01", capacidad=20, costo_operacion=0)]
    rutas = [
        DatosRuta(origen="E01", destino="P01", distancia_km=10, costo_km_t=None, habilitada=True),
        DatosRuta(origen="E02", destino="P01", distancia_km=12, costo_km_t=None, habilitada=False),
    ]

    resultado = validador.validar(construir_red(empresas, plantas, rutas, costo_km_global=350))

    assert resultado.nodos_aislados == ["E02"]
    assert resultado.es_valida() is False
    assert "Nodo aislado" in resultado.mensajes[-1]


def test_ruta_sin_distancia_no_se_habilita() -> None:
    empresas = [DatosEmpresa(codigo="E01", oferta=10)]
    plantas = [DatosPlanta(codigo="P01", capacidad=20, costo_operacion=0)]
    rutas = [
        DatosRuta(origen="E01", destino="P01", distancia_km=None, costo_km_t=None, habilitada=True)
    ]

    red = construir_red(empresas, plantas, rutas, costo_km_global=350)

    assert not red.rutas_habilitadas[0, 0]
    assert validador.validar(red).nodos_aislados == ["E01"]
