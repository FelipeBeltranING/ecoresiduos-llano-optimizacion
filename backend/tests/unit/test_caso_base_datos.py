from app.services.caso_base_datos import DISTANCIAS_KM, EMPRESAS, ORDEN_PLANTAS, PLANTAS


def test_caso_base_tiene_10_empresas_4_plantas_y_40_distancias() -> None:
    total_distancias = 0
    for distancias in DISTANCIAS_KM.values():
        total_distancias = total_distancias + len(distancias)

    assert len(EMPRESAS) == 10
    assert len(PLANTAS) == 4
    assert len(ORDEN_PLANTAS) == 4
    assert total_distancias == 40


def test_oferta_y_capacidad_totales() -> None:
    oferta_total = 0
    for empresa in EMPRESAS:
        oferta_total = oferta_total + empresa["oferta_t"]

    capacidad_total = 0
    for planta in PLANTAS:
        capacidad_total = capacidad_total + planta["capacidad_t"]

    assert oferta_total == 890
    assert capacidad_total == 950


def test_distancias_completas_y_positivas() -> None:
    for empresa in EMPRESAS:
        distancias = DISTANCIAS_KM[empresa["codigo"]]
        assert len(distancias) == 4
        for distancia in distancias:
            assert distancia > 0
