"""Índice de Criticidad Estructural (ICE) aplicado a la red logística (HU-20).

Adaptación de ICE(i) = α·C_B(i) + β·C_D⁻(i) + γ·(1 − R(i)) de Vega-Linares, Beltrán-Tabares
et al. (CICI 2026), propuesto para grafos de dependencias de microservicios. Aquí los nodos
son plantas y acopios, y el "fallo" es cerrar el nodo (capacidad 0) y volver a optimizar.
"""

from dataclasses import dataclass, field
from itertools import product

import numpy as np
from scipy.stats import spearmanr

from app.optimizacion.caminos import construir_caminos
from app.optimizacion.red import CODIGO_PLANTA_FICTICIA, RedLogistica, copiar_red
from app.optimizacion.sensibilidad.analizador import balancear, resolver_lp

PESOS_DEL_ARTICULO = (0.5, 0.3, 0.2)
UMBRAL_HOLGURA = 0.10  # mecanismo 1: al menos 10 % de capacidad libre
UMBRAL_RANGO = 0.10  # mecanismo 3: la capacidad puede bajar 10 % sin cambiar los duales
UMBRAL_ALTERNATIVA = 0.10  # mecanismo 4: segunda ruta a no más de 10 % de costo
TOLERANCIA = 1e-6
MECANISMOS = (
    "Holgura de capacidad",
    "Precio sombra 0",
    "Rango de estabilidad amplio",
    "Rutas alternativas",
    "Respaldo por acopio",
)


@dataclass
class CriticidadNodo:
    codigo: str
    tipo: str  # PLANTA o ACOPIO
    intermediacion: float  # C_B
    grado_entrada: float  # C_D⁻
    resiliencia: float  # R
    mecanismos: list[bool]
    ice: float = 0.0
    delta_costo_pct: float = 0.0  # impacto observado al cerrar el nodo
    toneladas_sin_planta: float = 0.0


@dataclass
class AnalisisCriticidad:
    pesos: tuple[float, float, float]
    costo_base: float
    nodos: list[CriticidadNodo]
    spearman: float | None
    pesos_calibrados: tuple[float, float, float] | None = None
    spearman_calibrado: float | None = None
    notas: list[str] = field(default_factory=list)


# ---------- Datos de la solución base que usan los tres términos ----------


@dataclass
class _Base:
    red: RedLogistica  # balanceada (con ficticia si hace falta)
    caminos: object
    flujos_caminos: np.ndarray
    duales: np.ndarray  # duales de capacidad por recurso (plantas y luego acopios)
    uso: np.ndarray  # toneladas por recurso
    costo: float


def _resolver_base(red: RedLogistica, penalizacion: float) -> _Base:
    balanceada = balancear(red, penalizacion)
    solucion = resolver_lp(balanceada)
    if solucion is None:
        raise ValueError("La red no tiene solución factible")
    caminos = construir_caminos(balanceada)
    uso = caminos.recursos.astype(float) @ solucion.flujos_caminos.sum(axis=0)
    return _Base(
        balanceada,
        caminos,
        solucion.flujos_caminos,
        solucion.duales_recursos,
        uso,
        solucion.costo,
    )


def _recursos_reales(red: RedLogistica) -> list[tuple[int, str, str]]:
    """(índice del recurso, código, tipo) de las plantas reales y los acopios."""
    lista = [
        (j, codigo, "PLANTA")
        for j, codigo in enumerate(red.codigos_plantas)
        if codigo != CODIGO_PLANTA_FICTICIA
    ]
    n = red.numero_plantas()
    lista += [(n + t, codigo, "ACOPIO") for t, codigo in enumerate(red.codigos_acopios)]
    return lista


# ---------- C_B: intermediación ----------


def _intermediacion(base: _Base, recurso: int, tipo: str) -> float:
    total = base.flujos_caminos.sum()
    if total <= 0:
        return 0.0
    if tipo == "PLANTA":
        # En un grafo bipartito la intermediación clásica es 0: se usa el flujo intermediado
        return float(base.uso[recurso] / total)
    return _intermediacion_de_acopio(base, recurso)


def _intermediacion_de_acopio(base: _Base, recurso: int) -> float:
    """Fracción de pares empresa → planta cuyo camino más barato pasa por el acopio."""
    caminos = base.caminos
    costos = np.where(caminos.habilitadas, caminos.costos, np.inf)
    pares = pasan = 0
    for i in range(costos.shape[0]):
        for planta in np.unique(caminos.planta_de):
            if base.red.codigos_plantas[planta] == CODIGO_PLANTA_FICTICIA:
                continue
            columnas = np.flatnonzero(caminos.planta_de == planta)
            mejor = costos[i, columnas].min()
            if not np.isfinite(mejor):
                continue
            pares += 1
            ganadores = columnas[np.isclose(costos[i, columnas], mejor)]
            pasan += np.mean([caminos.recursos[recurso, k] for k in ganadores])
    return float(pasan / pares) if pares else 0.0


# ---------- C_D⁻: grado de entrada ----------


def _empresas_que_dependen(base: _Base, recurso: int) -> np.ndarray:
    usa = base.caminos.recursos[recurso]
    return np.flatnonzero((base.flujos_caminos[:, usa] > TOLERANCIA).any(axis=1))


# ---------- R: resiliencia logística (5 mecanismos) ----------


def _capacidad(red: RedLogistica, recurso: int) -> float:
    n = red.numero_plantas()
    return float(red.capacidad[recurso] if recurso < n else red.capacidad_acopios[recurso - n])


def _con_capacidad(red: RedLogistica, recurso: int, valor: float) -> RedLogistica:
    nueva = copiar_red(red)
    n = nueva.numero_plantas()
    if recurso < n:
        nueva.capacidad[recurso] = valor
    else:
        nueva.capacidad_acopios[recurso - n] = valor
    return nueva


def _mecanismos(base: _Base, recurso: int) -> list[bool]:
    red, caminos = base.red, base.caminos
    capacidad = _capacidad(red, recurso)

    # 1. Holgura de capacidad (redundancia)
    holgura = capacidad > 0 and (capacidad - base.uso[recurso]) / capacidad >= UMBRAL_HOLGURA

    # 2. Precio sombra 0: no es cuello de botella
    sin_precio_sombra = abs(base.duales[recurso]) < 1e-4

    # 3. Rango amplio: bajar 10 % la capacidad no cambia los precios sombra
    reducida = resolver_lp(_con_capacidad(red, recurso, capacidad * (1 - UMBRAL_RANGO)))
    rango_amplio = reducida is not None and np.allclose(
        reducida.duales_recursos, base.duales, atol=1e-4
    )

    # 4. Rutas alternativas (análogo de los reintentos)
    dependientes = _empresas_que_dependen(base, recurso)
    con_alternativa = 0
    costos = np.where(caminos.habilitadas, caminos.costos, np.inf)
    no_usan = ~caminos.recursos[recurso]
    for i in dependientes:
        usados = caminos.recursos[recurso] & (base.flujos_caminos[i] > TOLERANCIA)
        costo_actual = costos[i, usados].min()
        alternativa = costos[i, no_usan].min() if no_usan.any() else np.inf
        if alternativa <= costo_actual * (1 + UMBRAL_ALTERNATIVA):
            con_alternativa += 1
    alternativas = len(dependientes) > 0 and con_alternativa >= len(dependientes) / 2

    # 5. Respaldo por acopio (análogo del circuit breaker): otro acopio con cupo
    n = red.numero_plantas()
    respaldo = False
    for t in range(red.numero_acopios()):
        otro = n + t
        if otro != recurso and _capacidad(red, otro) - base.uso[otro] > TOLERANCIA:
            respaldo = True

    return [bool(holgura), bool(sin_precio_sombra), bool(rango_amplio), alternativas, respaldo]


# ---------- Fallo simulado: cerrar el nodo y re-optimizar ----------


def simular_falla(red: RedLogistica, codigo: str, penalizacion: float) -> tuple[float, float]:
    """Costo y toneladas que quedan sin planta (ficticia) al cerrar el nodo."""
    indice = {c: r for r, c, _ in _recursos_reales(red)}[codigo]
    cerrada = balancear(_con_capacidad(red, indice, 0.0), penalizacion)
    solucion = resolver_lp(cerrada)
    if solucion is None:
        return float("inf"), float(red.oferta.sum())
    sin_planta = 0.0
    if cerrada.tiene_planta_ficticia():
        columna = cerrada.codigos_plantas.index(CODIGO_PLANTA_FICTICIA)
        sin_planta = float(solucion.flujos[:, columna].sum())
    return solucion.costo, sin_planta


# ---------- ICE, ranking y calibración ----------


def _ice(nodo: CriticidadNodo, pesos: tuple[float, float, float]) -> float:
    alfa, beta, gamma = pesos
    return alfa * nodo.intermediacion + beta * nodo.grado_entrada + gamma * (1 - nodo.resiliencia)


def correlacion(nodos: list[CriticidadNodo], pesos: tuple[float, float, float]) -> float | None:
    """ρ de Spearman entre el ICE y el impacto observado (aumento de costo al cerrar)."""
    if len(nodos) < 3:
        return None
    ice = [_ice(nodo, pesos) for nodo in nodos]
    impacto = [nodo.delta_costo_pct for nodo in nodos]
    if len(set(ice)) == 1 or len(set(impacto)) == 1:
        return None
    return float(spearmanr(ice, impacto).statistic)


def calibrar(nodos: list[CriticidadNodo], paso: float = 0.1):
    """Malla de (α, β, γ) con α + β + γ = 1 que maximiza ρ (los incidentes son las fallas)."""
    mejor = (None, None)
    pasos = int(round(1 / paso))
    for a, b in product(range(pasos + 1), repeat=2):
        if a + b > pasos:
            continue
        pesos = (a / pasos, b / pasos, (pasos - a - b) / pasos)
        rho = correlacion(nodos, pesos)
        if rho is not None and (mejor[1] is None or rho > mejor[1] + 1e-12):
            mejor = (pesos, rho)
    return mejor


def calcular_ice(
    red: RedLogistica,
    penalizacion: float,
    pesos: tuple[float, float, float] = PESOS_DEL_ARTICULO,
) -> AnalisisCriticidad:
    if abs(sum(pesos) - 1) > 1e-6 or min(pesos) < 0:
        raise ValueError("Los pesos α, β y γ deben ser no negativos y sumar 1")
    base = _resolver_base(red, penalizacion)

    # Paso 1: los tres términos de cada planta y acopio
    nodos = []
    for recurso, codigo, tipo in _recursos_reales(base.red):
        mecanismos = _mecanismos(base, recurso)
        nodo = CriticidadNodo(
            codigo=codigo,
            tipo=tipo,
            intermediacion=_intermediacion(base, recurso, tipo),
            grado_entrada=len(_empresas_que_dependen(base, recurso)) / red.numero_empresas(),
            resiliencia=sum(mecanismos) / len(mecanismos),
            mecanismos=mecanismos,
        )
        nodo.ice = _ice(nodo, pesos)
        # Paso 2: impacto observado al cerrar el nodo
        costo, sin_planta = simular_falla(red, codigo, penalizacion)
        nodo.delta_costo_pct = (costo - base.costo) / base.costo * 100
        nodo.toneladas_sin_planta = sin_planta
        nodos.append(nodo)

    # Paso 3: ranking, correlación con el impacto y pesos que mejor lo explican
    nodos.sort(key=lambda nodo: nodo.ice, reverse=True)
    pesos_calibrados, rho_calibrado = calibrar(nodos)
    analisis = AnalisisCriticidad(
        pesos=pesos,
        costo_base=base.costo,
        nodos=nodos,
        spearman=correlacion(nodos, pesos),
        pesos_calibrados=pesos_calibrados,
        spearman_calibrado=rho_calibrado,
    )
    if len(nodos) < 5:
        analisis.notas.append(
            f"Solo {len(nodos)} nodos: la correlación es evidencia preliminar, no concluyente."
        )
    return analisis
