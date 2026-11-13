
import time
from dataclasses import dataclass

import numpy as np

from app.optimizacion.red import RedLogistica, copiar_red

COSTO_PROHIBIDO = 1e12
TOLERANCIA = 1e-9
MAX_ITERACIONES = 50_000
MAX_BASES_RECORDADAS = 5_000

ESTADO_OPTIMO = "Óptimo"
ESTADO_INFACTIBLE = "Infactible"


@dataclass
class ModeloExpandido:
    costos: np.ndarray
    oferta: np.ndarray
    demanda: np.ndarray
    acopios_activos: list[int]
    fila_holgura: int | None


def expandir(red: RedLogistica) -> ModeloExpandido | None:
    m = red.numero_empresas()
    n = red.numero_plantas()
    t_total = red.numero_acopios()
    capacidad_total = float(red.capacidad.sum())
    oferta_total = float(red.oferta.sum())

    if oferta_total > capacidad_total + TOLERANCIA:
        return None

    acopios = [
        k
        for k in range(t_total)
        if red.capacidad_acopios[k] > TOLERANCIA
        and bool(red.rutas_a_acopio[:, k].any())
        and bool(red.rutas_desde_acopio[k, :].any())
    ]
    t = len(acopios)

    filas = m + t
    columnas = n + t
    holgura = capacidad_total - oferta_total
    fila_holgura = None
    columna_ajuste = None
    if holgura > TOLERANCIA:
        fila_holgura = filas
        filas += 1
    elif holgura < -TOLERANCIA:
        return None
    elif holgura < 0:
        columna_ajuste = columnas
        columnas += 1

    costos = np.full((filas, columnas), COSTO_PROHIBIDO)
    oferta = np.zeros(filas)
    demanda = np.zeros(columnas)
    oferta[:m] = red.oferta
    demanda[:n] = red.capacidad

    if fila_holgura is not None:
        oferta[fila_holgura] = holgura
        costos[fila_holgura, :n] = 0.0
    if columna_ajuste is not None:
        demanda[columna_ajuste] = -holgura
        costos[:, columna_ajuste] = 0.0

    for p, k in enumerate(acopios):
        fila = m + p
        columna = n + p
        oferta[fila] = red.capacidad_acopios[k]
        demanda[columna] = red.capacidad_acopios[k]
        costos[fila, columna] = 0.0

    for i in range(m):
        for j in range(n):
            if red.rutas_habilitadas[i, j]:
                costos[i, j] = red.costos[i, j]

    for p, k in enumerate(acopios):
        for i in range(m):
            if red.rutas_a_acopio[i, k]:
                costos[i, n + p] = red.costos_a_acopio[i, k]
        for j in range(n):
            if red.rutas_desde_acopio[k, j]:
                costos[m + p, j] = red.costos_desde_acopio[k, j]

    return ModeloExpandido(
        costos=costos,
        oferta=oferta,
        demanda=demanda,
        acopios_activos=acopios,
        fila_holgura=fila_holgura,
    )


def _flujo_factible(modelo: ModeloExpandido) -> np.ndarray | None:
    costos = modelo.costos
    m, n = costos.shape
    total = float(modelo.oferta.sum())
    if total <= TOLERANCIA:
        return np.zeros((m, n))

    nodos = m + n + 2
    origen = m + n
    destino = m + n + 1
    capacidad = np.zeros((nodos, nodos))
    for i in range(m):
        capacidad[origen, i] = modelo.oferta[i]
    for j in range(n):
        capacidad[m + j, destino] = modelo.demanda[j]
    permitidas = costos < COSTO_PROHIBIDO / 2
    for i in range(m):
        for j in range(n):
            if permitidas[i, j]:
                capacidad[i, m + j] = min(modelo.oferta[i], modelo.demanda[j])

    flujo = np.zeros((nodos, nodos))
    enviado = 0.0
    while enviado < total - TOLERANCIA:
        padre = [-1] * nodos
        padre[origen] = origen
        cola = [origen]
        while cola and padre[destino] == -1:
            u = cola.pop(0)
            for v in range(nodos):
                if padre[v] == -1 and capacidad[u, v] - flujo[u, v] > TOLERANCIA:
                    padre[v] = u
                    cola.append(v)
                    if v == destino:
                        break
        if padre[destino] == -1:
            break

        delta = total - enviado
        v = destino
        while v != origen:
            u = padre[v]
            delta = min(delta, capacidad[u, v] - flujo[u, v])
            v = u
        v = destino
        while v != origen:
            u = padre[v]
            flujo[u, v] += delta
            flujo[v, u] -= delta
            v = u
        enviado += delta

    if enviado < total - 1e-6:
        return None

    solucion = flujo[:m, m : m + n].copy()
    solucion[np.abs(solucion) < TOLERANCIA] = 0.0
    return solucion


def _buscar_ciclo(x: np.ndarray, m: int, n: int) -> list[int] | None:
    adyacencia = [[] for _ in range(m + n)]
    for i in range(m):
        for j in range(n):
            if x[i, j] > TOLERANCIA:
                adyacencia[i].append(m + j)
                adyacencia[m + j].append(i)

    padre = [-2] * (m + n)
    en_pila = [False] * (m + n)
    for inicio in range(m + n):
        if padre[inicio] != -2 or not adyacencia[inicio]:
            continue
        padre[inicio] = -1
        en_pila[inicio] = True
        pila = [(inicio, iter(adyacencia[inicio]))]
        while pila:
            u, iterador = pila[-1]
            v = next(iterador, None)
            if v is None:
                en_pila[u] = False
                pila.pop()
                continue
            if padre[v] == -2:
                padre[v] = u
                en_pila[v] = True
                pila.append((v, iter(adyacencia[v])))
            elif en_pila[v] and padre[u] != v:
                camino = []
                a = u
                while a != v:
                    camino.append(a)
                    a = padre[a]
                camino.append(v)
                camino.reverse()
                return camino
    return None


def _reducir_a_forest(x: np.ndarray, m: int, n: int) -> np.ndarray:
    x = x.copy()
    while True:
        ciclo = _buscar_ciclo(x, m, n)
        if ciclo is None:
            return x

        aristas = []
        for k, a in enumerate(ciclo):
            b = ciclo[(k + 1) % len(ciclo)]
            aristas.append((a, b - m) if a < m else (b, a - m))
        signos = [1 if k % 2 == 0 else -1 for k in range(len(aristas))]
        theta = min(x[i, j] for (i, j), signo in zip(aristas, signos, strict=True) if signo < 0)
        for (i, j), signo in zip(aristas, signos, strict=True):
            x[i, j] += signo * theta
            if abs(x[i, j]) < 1e-7:
                x[i, j] = 0.0


def _extender_a_arbol(x: np.ndarray, costos: np.ndarray) -> set[tuple[int, int]]:
    m, n = x.shape
    basicas = {(i, j) for i in range(m) for j in range(n) if x[i, j] > TOLERANCIA}
    padre = list(range(m + n))

    def encontrar(a: int) -> int:
        while padre[a] != a:
            padre[a] = padre[padre[a]]
            a = padre[a]
        return a

    def unir(a: int, b: int) -> bool:
        ra, rb = encontrar(a), encontrar(b)
        if ra == rb:
            return False
        padre[rb] = ra
        return True

    for i, j in basicas:
        unir(i, m + j)

    candidatas = sorted(
        (costos[i, j], i, j)
        for i in range(m)
        for j in range(n)
        if costos[i, j] < COSTO_PROHIBIDO / 2 and (i, j) not in basicas
    )
    for _, i, j in candidatas:
        if unir(i, m + j):
            basicas.add((i, j))
    return basicas


def _potenciales(
    basicas: set[tuple[int, int]], costos: np.ndarray, m: int, n: int
) -> tuple[np.ndarray, np.ndarray]:
    adyacencia = [[] for _ in range(m + n)]
    for i, j in basicas:
        adyacencia[i].append(m + j)
        adyacencia[m + j].append(i)

    u = np.zeros(m)
    v = np.zeros(n)
    visitado = [False] * (m + n)
    for inicio in range(m + n):
        if visitado[inicio] or not adyacencia[inicio]:
            continue
        visitado[inicio] = True
        pila = [inicio]
        while pila:
            a = pila.pop()
            for b in adyacencia[a]:
                if visitado[b]:
                    continue
                if a < m:
                    v[b - m] = costos[a, b - m] - u[a]
                else:
                    u[b] = costos[b, a - m] - v[a - m]
                visitado[b] = True
                pila.append(b)
    return u, v


def _componentes(
    basicas: set[tuple[int, int]], oferta: np.ndarray, m: int, n: int
) -> tuple[list[int], list[float]]:
    adyacencia = [[] for _ in range(m + n)]
    for i, j in basicas:
        adyacencia[i].append(m + j)
        adyacencia[m + j].append(i)

    componente = [-1] * (m + n)
    totales = []
    for inicio in range(m + n):
        if componente[inicio] != -1 or not adyacencia[inicio]:
            continue
        identificador = len(totales)
        componente[inicio] = identificador
        pila = [inicio]
        total = 0.0
        while pila:
            a = pila.pop()
            if a < m:
                total += float(oferta[a])
            for b in adyacencia[a]:
                if componente[b] == -1:
                    componente[b] = identificador
                    pila.append(b)
        totales.append(total)
    return componente, totales


def _camino(
    basicas: set[tuple[int, int]], m: int, n: int, fila: int, columna: int
) -> list[int] | None:
    adyacencia = [[] for _ in range(m + n)]
    for i, j in basicas:
        adyacencia[i].append(m + j)
        adyacencia[m + j].append(i)

    inicio = fila
    meta = m + columna
    padre = {inicio: None}
    pila = [inicio]
    while pila:
        a = pila.pop()
        if a == meta:
            break
        for b in adyacencia[a]:
            if b not in padre:
                padre[b] = a
                pila.append(b)
    if meta not in padre:
        return None

    camino = []
    a = meta
    while a is not None:
        camino.append(a)
        a = padre[a]
    camino.reverse()
    return camino


def _resolver_expandido(
    modelo: ModeloExpandido,
) -> tuple[np.ndarray, set[tuple[int, int]]] | None:
    m, n = modelo.costos.shape
    if modelo.oferta.sum() <= TOLERANCIA:
        return np.zeros((m, n)), set()

    x = _flujo_factible(modelo)
    if x is None:
        return None
    x = _reducir_a_forest(x, m, n)
    basicas = _extender_a_arbol(x, modelo.costos)

    blando = False
    vistos: set[frozenset[tuple[int, int]]] = set()
    for _ in range(MAX_ITERACIONES):
        firma = frozenset(basicas)
        if firma in vistos:
            blando = True
        if len(vistos) < MAX_BASES_RECORDADAS:
            vistos.add(firma)

        u, v = _potenciales(basicas, modelo.costos, m, n)
        componente, totales = _componentes(basicas, modelo.oferta, m, n)
        mejor = None
        for i in range(m):
            if componente[i] < 0 or totales[componente[i]] <= TOLERANCIA:
                continue
            for j in range(n):
                if modelo.costos[i, j] >= COSTO_PROHIBIDO / 2 or (i, j) in basicas:
                    continue
                if componente[i] != componente[m + j]:
                    continue
                delta = modelo.costos[i, j] - u[i] - v[j]
                if delta < -1e-7 and (mejor is None or delta < mejor[0]):
                    mejor = (delta, i, j)
                    if blando:
                        break
            if blando and mejor is not None:
                break
        if mejor is None:
            return x, basicas

        _, fila, columna = mejor
        camino = _camino(basicas, m, n, fila, columna)
        if camino is None:
            return None

        celdas = [(fila, columna)]
        for a, b in zip(camino, camino[1:], strict=False):
            celdas.append((a, b - m) if a < m else (b, a - m))
        signos = [1 if k % 2 == 0 else -1 for k in range(len(celdas))]
        theta = min(x[i, j] for (i, j), signo in zip(celdas, signos, strict=True) if signo < 0)
        for (i, j), signo in zip(celdas, signos, strict=True):
            x[i, j] += signo * theta
            if abs(x[i, j]) < 1e-7:
                x[i, j] = 0.0

        basicas.add((fila, columna))
        saliente = None
        for (i, j), signo in zip(celdas[1:], signos[1:], strict=True):
            if signo < 0 and x[i, j] <= TOLERANCIA:
                saliente = (i, j)
                break
        if saliente is None:
            return None
        basicas.remove(saliente)

    return None


def _costo_optimo(red: RedLogistica) -> float | None:
    modelo = expandir(red)
    if modelo is None:
        return None
    solucion = _resolver_expandido(modelo)
    if solucion is None:
        return None
    x, _ = solucion
    return float((x * modelo.costos).sum())


def _duales_capacidad(red: RedLogistica, holguras: np.ndarray, costo_base: float) -> np.ndarray:
    duales = np.zeros(red.numero_plantas())
    for j in range(red.numero_plantas()):
        if holguras[j] > TOLERANCIA:
            continue
        prueba = copiar_red(red)
        prueba.capacidad[j] += 1.0
        costo = _costo_optimo(prueba)
        if costo is not None:
            duales[j] = costo - costo_base
    duales[np.abs(duales) < 1e-6] = 0.0
    return duales


def _duales_acopio(red: RedLogistica, holguras: np.ndarray, costo_base: float) -> np.ndarray:
    duales = np.zeros(red.numero_acopios())
    for k in range(red.numero_acopios()):
        if holguras[k] > TOLERANCIA:
            continue
        if not red.rutas_a_acopio[:, k].any() or not red.rutas_desde_acopio[k, :].any():
            continue
        prueba = copiar_red(red)
        prueba.capacidad_acopios[k] += 1.0
        costo = _costo_optimo(prueba)
        if costo is not None:
            duales[k] = costo - costo_base
    duales[np.abs(duales) < 1e-6] = 0.0
    return duales


def _duales_oferta(modelo: ModeloExpandido, basicas: set[tuple[int, int]]) -> np.ndarray:
    filas, columnas = modelo.costos.shape
    m = filas - len(modelo.acopios_activos)
    if modelo.fila_holgura is not None:
        m -= 1
    u, _ = _potenciales(basicas, modelo.costos, filas, columnas)
    if modelo.fila_holgura is not None:
        return (u[:m] - u[modelo.fila_holgura]).copy()
    return u[:m].copy()


def _costos_reducidos(
    red: RedLogistica,
    modelo: ModeloExpandido,
    basicas: set[tuple[int, int]],
) -> np.ndarray:
    m, n = red.numero_empresas(), red.numero_plantas()
    filas, columnas = modelo.costos.shape
    u, v = _potenciales(basicas, modelo.costos, filas, columnas)
    reducidos = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            if not red.rutas_habilitadas[i, j]:
                continue
            valor = red.costos[i, j] - u[i] - v[j]
            reducidos[i, j] = 0.0 if abs(valor) < 1e-6 else valor
    return reducidos


class ModeloTransbordo:
    def __init__(self, red: RedLogistica) -> None:
        self.red = red

    def resolver(self) -> dict:
        inicio = time.perf_counter()
        red = self.red
        m, n = red.numero_empresas(), red.numero_plantas()

        modelo = expandir(red)
        solucion = _resolver_expandido(modelo) if modelo is not None else None
        if solucion is None:
            resultado = self._resultado_infactible(red)
            resultado["tiempo_ms"] = (time.perf_counter() - inicio) * 1000
            return resultado

        x, basicas = solucion
        flujos = x[:m, :n].copy()
        flujos[np.abs(flujos) < TOLERANCIA] = 0.0

        flujos_a_acopio = np.zeros((m, red.numero_acopios()))
        flujos_desde_acopio = np.zeros((red.numero_acopios(), n))
        for p, k in enumerate(modelo.acopios_activos):
            flujos_a_acopio[:, k] = x[:m, n + p]
            flujos_desde_acopio[k, :] = x[m + p, :n]

        recibido = flujos.sum(axis=0) + flujos_desde_acopio.sum(axis=0)
        holguras = red.capacidad - recibido
        holguras[np.abs(holguras) < 1e-7] = 0.0

        costo_total = float((x * modelo.costos).sum())
        duales_oferta = _duales_oferta(modelo, basicas)
        duales_capacidad = _duales_capacidad(red, holguras, costo_total)
        costos_reducidos = _costos_reducidos(red, modelo, basicas)

        resultado = {
            "estado": ESTADO_OPTIMO,
            "costo_total": costo_total,
            "flujos": flujos,
            "duales_oferta": duales_oferta,
            "duales_capacidad": duales_capacidad,
            "costos_reducidos": costos_reducidos,
            "holguras": holguras,
        }

        if red.tiene_acopios():
            holguras_acopio = red.capacidad_acopios - flujos_a_acopio.sum(axis=0)
            holguras_acopio[np.abs(holguras_acopio) < 1e-7] = 0.0
            resultado.update(
                {
                    "flujos_a_acopio": flujos_a_acopio,
                    "flujos_desde_acopio": flujos_desde_acopio,
                    "duales_acopio": _duales_acopio(red, holguras_acopio, costo_total),
                    "holguras_acopio": holguras_acopio,
                }
            )

        resultado["tiempo_ms"] = (time.perf_counter() - inicio) * 1000
        return resultado

    def _resultado_infactible(self, red: RedLogistica) -> dict:
        m, n = red.numero_empresas(), red.numero_plantas()
        resultado = {
            "estado": ESTADO_INFACTIBLE,
            "costo_total": 0.0,
            "flujos": np.zeros((m, n)),
            "duales_oferta": np.zeros(m),
            "duales_capacidad": np.zeros(n),
            "costos_reducidos": np.zeros((m, n)),
            "holguras": red.capacidad.copy(),
        }
        if red.tiene_acopios():
            t = red.numero_acopios()
            resultado.update(
                {
                    "flujos_a_acopio": np.zeros((m, t)),
                    "flujos_desde_acopio": np.zeros((t, n)),
                    "duales_acopio": np.zeros(t),
                    "holguras_acopio": red.capacidad_acopios.copy(),
                }
            )
        return resultado
