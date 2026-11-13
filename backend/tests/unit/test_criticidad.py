
import pytest

from app.optimizacion.criticidad import CriticidadNodo, _ice, calcular_ice, simular_falla
from app.optimizacion.red import DatosEmpresa, DatosPlanta, DatosRuta, construir_red
from app.services.caso_real_service import leer_caso_real
from tests.utilidades import PENALIZACION_FICTICIA, construir_red_caso_base


@pytest.fixture(scope="module")
def analisis_caso_base():
    return calcular_ice(construir_red_caso_base(), PENALIZACION_FICTICIA)


def red_caso_real():
    caso = leer_caso_real()
    empresas = [DatosEmpresa(e["codigo"], e["oferta_t"]) for e in caso["empresas"]]
    plantas = [
        DatosPlanta(p["codigo"], p["capacidad_t"], p["costo_operacion_t"]) for p in caso["plantas"]
    ]
    rutas = [
        DatosRuta(r["origen"], r["destino"], r["distancia_km"], None, True) for r in caso["rutas"]
    ]
    return construir_red(empresas, plantas, rutas, 350)


def test_ice_esta_entre_cero_y_uno(analisis_caso_base) -> None:
    for nodo in analisis_caso_base.nodos:
        assert 0 <= nodo.ice <= 1
        assert 0 <= nodo.resiliencia <= 1


def test_pesos_deben_sumar_uno() -> None:
    with pytest.raises(ValueError):
        calcular_ice(construir_red_caso_base(), PENALIZACION_FICTICIA, (0.5, 0.5, 0.5))


def test_mas_resiliencia_nunca_aumenta_la_criticidad() -> None:
    fragil = CriticidadNodo("X", "PLANTA", 0.3, 0.4, 0.0, [False] * 5)
    resiliente = CriticidadNodo("Y", "PLANTA", 0.3, 0.4, 1.0, [True] * 5)
    assert _ice(resiliente, (0.5, 0.3, 0.2)) < _ice(fragil, (0.5, 0.3, 0.2))


def test_ranking_del_caso_base(analisis_caso_base) -> None:
    assert [n.codigo for n in analisis_caso_base.nodos] == ["P01", "P03", "P02", "P04"]
    assert analisis_caso_base.spearman == pytest.approx(0.8)


def test_cerrar_villavicencio_deja_240_t_sin_planta() -> None:
    _, sin_planta = simular_falla(construir_red_caso_base(), "P01", PENALIZACION_FICTICIA)
    assert sin_planta == pytest.approx(240)


def test_caso_real_el_ice_ordena_igual_que_el_impacto() -> None:
    analisis = calcular_ice(red_caso_real(), PENALIZACION_FICTICIA)
    assert analisis.spearman == pytest.approx(1.0)


def test_calibracion_no_empeora_la_correlacion(analisis_caso_base) -> None:
    assert analisis_caso_base.spearman_calibrado >= analisis_caso_base.spearman
    assert sum(analisis_caso_base.pesos_calibrados) == pytest.approx(1)


def test_con_acopios_tambien_se_evaluan_los_acopios() -> None:
    analisis = calcular_ice(construir_red_caso_base(con_acopios=True), PENALIZACION_FICTICIA)
    tipos = {n.codigo: n.tipo for n in analisis.nodos}
    assert tipos["A01"] == "ACOPIO"
    assert tipos["A02"] == "ACOPIO"
