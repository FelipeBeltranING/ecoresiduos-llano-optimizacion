import uuid

import numpy as np
import pytest
from pydantic import ValidationError

from app.schemas.analisis import ComparacionEntrada
from app.services.analisis_service import cambio_de_asignacion, ids_de_escenarios


# Los diez escenarios por defecto salen del criterio de HU-13
def test_la_comparacion_usa_diez_corridas_por_defecto() -> None:
    assert ComparacionEntrada().corridas == 10


def test_los_escenarios_no_se_repiten() -> None:
    primero, segundo = uuid.uuid4(), uuid.uuid4()

    datos = ComparacionEntrada(escenario_id=primero, escenarios=[primero, segundo])

    assert ids_de_escenarios(datos) == [primero, segundo]


def test_no_se_admiten_mas_de_seis_escenarios() -> None:
    with pytest.raises(ValidationError):
        ComparacionEntrada(escenarios=[uuid.uuid4() for _ in range(7)])


def test_cambio_de_asignacion_es_cero_sin_cambios() -> None:
    flujos = np.array([[10.0, 0.0], [0.0, 5.0]])

    assert cambio_de_asignacion(flujos, flujos) == pytest.approx(0.0)


def test_cambio_de_asignacion_mide_las_toneladas_movidas() -> None:
    base = np.array([[10.0, 0.0], [0.0, 5.0]])
    movido = np.array([[0.0, 10.0], [0.0, 5.0]])

    assert cambio_de_asignacion(base, movido) == pytest.approx(100 * 10 / 15)


def test_cambio_de_asignacion_total_si_desaparece_la_asignacion() -> None:
    base = np.array([[10.0, 0.0], [0.0, 5.0]])

    assert cambio_de_asignacion(base, np.zeros((2, 2))) == pytest.approx(100.0)


def test_cambio_de_asignacion_sin_flujo_devuelve_cero() -> None:
    assert cambio_de_asignacion(np.zeros((2, 2)), np.zeros((2, 2))) == 0.0
