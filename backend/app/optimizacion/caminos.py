"""Red vista por caminos (HU-17).

Un camino es `empresa → planta` o `empresa → acopio → planta` y su costo es la suma de sus
arcos. Con esta vista el AG y la re-optimización siguen trabajando con una matriz
empresa × camino; sin acopios, los caminos son exactamente las plantas.
"""

from dataclasses import dataclass

import numpy as np

from app.optimizacion.red import RedLogistica

SIN_ACOPIO = -1


@dataclass
class RedPorCaminos:
    costos: np.ndarray  # empresa × camino
    habilitadas: np.ndarray  # empresa × camino
    planta_de: np.ndarray  # planta donde termina cada camino
    acopio_de: np.ndarray  # acopio por el que pasa (SIN_ACOPIO si es directo)
    # recursos[r, k]: el camino k consume capacidad del recurso r (plantas y luego acopios)
    recursos: np.ndarray
    capacidad_recursos: np.ndarray


# Caminos de la red: primero los directos (uno por planta) y luego acopio × planta
def construir_caminos(red: RedLogistica) -> RedPorCaminos:
    m, n, t = red.numero_empresas(), red.numero_plantas(), red.numero_acopios()
    total = n + t * n

    costos = np.zeros((m, total))
    habilitadas = np.zeros((m, total), dtype=bool)
    planta_de = np.zeros(total, dtype=int)
    acopio_de = np.full(total, SIN_ACOPIO, dtype=int)
    recursos = np.zeros((n + t, total), dtype=bool)

    # Paso 1: caminos directos empresa → planta
    costos[:, :n] = red.costos
    habilitadas[:, :n] = red.rutas_habilitadas
    for planta in range(n):
        planta_de[planta] = planta
        recursos[planta, planta] = True

    # Paso 2: caminos empresa → acopio → planta (costo = suma de los dos arcos)
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


# Flujos por arco de una solución: directos, empresa → acopio y acopio → planta
@dataclass
class FlujosPorArco:
    directos: np.ndarray
    a_acopio: np.ndarray | None = None
    desde_acopio: np.ndarray | None = None


# Pasa una solución por caminos a flujos por arco (suma los caminos que usan cada arco)
def caminos_a_arcos(red: RedLogistica, flujos_caminos: np.ndarray) -> FlujosPorArco:
    m, n, t = red.numero_empresas(), red.numero_plantas(), red.numero_acopios()
    directos = flujos_caminos[:, :n].copy()
    if t == 0:
        return FlujosPorArco(directos)
    por_acopio = flujos_caminos[:, n:].reshape(m, t, n)
    return FlujosPorArco(directos, por_acopio.sum(axis=2), por_acopio.sum(axis=0))


# Toneladas de cada empresa que terminan en cada planta, sin importar el camino
def flujo_a_planta_final(red: RedLogistica, flujos_caminos: np.ndarray) -> np.ndarray:
    m, n, t = red.numero_empresas(), red.numero_plantas(), red.numero_acopios()
    if t == 0:
        return flujos_caminos.copy()
    return flujos_caminos[:, :n] + flujos_caminos[:, n:].reshape(m, t, n).sum(axis=1)


# Costo total de una solución dada por arcos
def costo_de_arcos(red: RedLogistica, flujos: FlujosPorArco) -> float:
    costo = float(np.sum(flujos.directos * red.costos))
    if red.tiene_acopios() and flujos.a_acopio is not None:
        costo += float(np.sum(flujos.a_acopio * red.costos_a_acopio))
        costo += float(np.sum(flujos.desde_acopio * red.costos_desde_acopio))
    return costo
