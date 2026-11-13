
from dataclasses import dataclass

import numpy as np

from app.optimizacion.red import RedLogistica

SIN_ACOPIO = -1


@dataclass
class RedPorCaminos:
    costos: np.ndarray
    habilitadas: np.ndarray
    planta_de: np.ndarray
    acopio_de: np.ndarray
    recursos: np.ndarray
    capacidad_recursos: np.ndarray


def construir_caminos(red: RedLogistica) -> RedPorCaminos:
    m, n, t = red.numero_empresas(), red.numero_plantas(), red.numero_acopios()
    total = n + t * n

    costos = np.zeros((m, total))
    habilitadas = np.zeros((m, total), dtype=bool)
    planta_de = np.zeros(total, dtype=int)
    acopio_de = np.full(total, SIN_ACOPIO, dtype=int)
    recursos = np.zeros((n + t, total), dtype=bool)

    costos[:, :n] = red.costos
    habilitadas[:, :n] = red.rutas_habilitadas
    for planta in range(n):
        planta_de[planta] = planta
        recursos[planta, planta] = True

    for acopio in range(t):
        for planta in range(n):
            camino = n + acopio * n + planta
            planta_de[camino] = planta
            acopio_de[camino] = acopio
            recursos[planta, camino] = True
            recursos[n + acopio, camino] = True
            if not red.rutas_desde_acopio[acopio, planta]:
                continue
            habilitadas[:, camino] = red.rutas_a_acopio[:, acopio]
            costos[:, camino] = np.where(
                red.rutas_a_acopio[:, acopio],
                red.costos_a_acopio[:, acopio] + red.costos_desde_acopio[acopio, planta],
                0.0,
            )

    capacidad = red.capacidad
    if t > 0:
        capacidad = np.concatenate([red.capacidad, red.capacidad_acopios])
    return RedPorCaminos(costos, habilitadas, planta_de, acopio_de, recursos, capacidad.copy())


@dataclass
class FlujosPorArco:
    directos: np.ndarray
    a_acopio: np.ndarray | None = None
    desde_acopio: np.ndarray | None = None


def caminos_a_arcos(red: RedLogistica, flujos_caminos: np.ndarray) -> FlujosPorArco:
    m, n, t = red.numero_empresas(), red.numero_plantas(), red.numero_acopios()
    directos = flujos_caminos[:, :n].copy()
    if t == 0:
        return FlujosPorArco(directos)
    por_acopio = flujos_caminos[:, n:].reshape(m, t, n)
    return FlujosPorArco(directos, por_acopio.sum(axis=2), por_acopio.sum(axis=0))


def flujo_a_planta_final(red: RedLogistica, flujos_caminos: np.ndarray) -> np.ndarray:
    m, n, t = red.numero_empresas(), red.numero_plantas(), red.numero_acopios()
    if t == 0:
        return flujos_caminos.copy()
    return flujos_caminos[:, :n] + flujos_caminos[:, n:].reshape(m, t, n).sum(axis=1)


def costo_de_arcos(red: RedLogistica, flujos: FlujosPorArco) -> float:
    costo = float(np.sum(flujos.directos * red.costos))
    if red.tiene_acopios() and flujos.a_acopio is not None:
        costo += float(np.sum(flujos.a_acopio * red.costos_a_acopio))
        costo += float(np.sum(flujos.desde_acopio * red.costos_desde_acopio))
    return costo
