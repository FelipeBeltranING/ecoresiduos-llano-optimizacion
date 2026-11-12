"""Escenarios de sensibilidad (HU-11) y rangos de estabilidad por re-optimización (HU-12)."""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog

from app.optimizacion.caminos import construir_caminos, flujo_a_planta_final
from app.optimizacion.red import RedLogistica, ValidadorRed, copiar_red, preparar_red_para_motor

TOLERANCIA_FLUJO = 1e-6
TOLERANCIA_DUAL = 1e-4
ITERACIONES_BISECCION = 14
# Por encima de este tamaño los rangos tardarían demasiado y se omiten
MAX_VARIABLES_RANGOS = 600

COSTO_TRANSPORTE = "COSTO_TRANSPORTE"
OFERTA = "OFERTA"
CAPACIDAD = "CAPACIDAD"
COSTO_RUTA = "COSTO_RUTA"
CERRAR_RUTA = "CERRAR_RUTA"
TIPOS_AJUSTE = (COSTO_TRANSPORTE, OFERTA, CAPACIDAD, COSTO_RUTA, CERRAR_RUTA)


# Un ajuste de escenario: porcentaje aplicado a un parámetro (objetivo vacío = todos)
@dataclass
class Ajuste:
    tipo: str
    porcentaje: float = 0.0
    objetivo: str | None = None


# Solución rápida con HiGHS (en proceso, sin CBC) para la re-optimización paramétrica
@dataclass
class SolucionLP:
    costo: float
    flujos: np.ndarray
    duales_oferta: np.ndarray
    duales_capacidad: np.ndarray


# Con acopios se resuelve por caminos; los flujos se devuelven por planta final (m x n)
def resolver_lp(red: RedLogistica) -> SolucionLP | None:
    m, n = red.numero_empresas(), red.numero_plantas()
    caminos = construir_caminos(red)
    total = caminos.costos.shape[1]
    indices = [(i, k) for i in range(m) for k in range(total) if caminos.habilitadas[i, k]]
    if not indices:
        return None
    c = np.array([caminos.costos[i, k] for i, k in indices])
    a_eq = np.zeros((m, len(indices)))
    a_ub = np.zeros((len(caminos.capacidad_recursos), len(indices)))
    for columna, (i, k) in enumerate(indices):
        a_eq[i, columna] = 1
        a_ub[:, columna] = caminos.recursos[:, k]
    res = linprog(
        c, A_ub=a_ub, b_ub=caminos.capacidad_recursos, A_eq=a_eq, b_eq=red.oferta, method="highs"
    )
    if not res.success:
        return None
    flujos_caminos = np.zeros((m, total))
    for columna, (i, k) in enumerate(indices):
        flujos_caminos[i, k] = res.x[columna]
    return SolucionLP(
        costo=float(res.fun),
        flujos=flujo_a_planta_final(red, flujos_caminos),
        duales_oferta=np.array(res.eqlin.marginals),
        duales_capacidad=np.array(res.ineqlin.marginals)[:n],
    )


def _filas(red: RedLogistica, objetivo: str | None) -> list[int]:
    if objetivo is None:
        return list(range(red.numero_empresas()))
    if objetivo not in red.codigos_empresas:
        raise ValueError(f"La empresa {objetivo} no está en la red")
    return [red.codigos_empresas.index(objetivo)]


def _columnas(red: RedLogistica, objetivo: str | None) -> list[int]:
    if objetivo is None:
        return list(range(red.numero_plantas()))
    if objetivo not in red.codigos_plantas:
        raise ValueError(f"La planta {objetivo} no está en la red")
    return [red.codigos_plantas.index(objetivo)]


def _ruta(red: RedLogistica, objetivo: str | None) -> tuple[int, int]:
    if not objetivo or "->" not in objetivo:
        raise ValueError("La ruta se indica como ORIGEN->DESTINO, por ejemplo E01->P01")
    origen, destino = (parte.strip() for parte in objetivo.split("->", 1))
    return _filas(red, origen)[0], _columnas(red, destino)[0]


# Aplica los ajustes de un escenario sobre una copia de la red (sin planta ficticia)
def aplicar_ajustes(red: RedLogistica, ajustes: list[Ajuste]) -> RedLogistica:
    nueva = copiar_red(red)
    for ajuste in ajustes:
        factor = 1 + ajuste.porcentaje / 100
        if ajuste.tipo == COSTO_TRANSPORTE:
            operacion = (
                np.zeros(nueva.numero_plantas())
                if nueva.costo_operacion is None
                else nueva.costo_operacion
            )
            transporte = nueva.costos - operacion[None, :]
            filas = _filas(nueva, ajuste.objetivo) if ajuste.objetivo else None
            nuevos = transporte * factor + operacion[None, :]
            if filas is None:
                nueva.costos = np.where(nueva.rutas_habilitadas, nuevos, nueva.costos)
            else:
                for i in filas:
                    nueva.costos[i] = np.where(nueva.rutas_habilitadas[i], nuevos[i], 0)
        elif ajuste.tipo == OFERTA:
            for i in _filas(nueva, ajuste.objetivo):
                nueva.oferta[i] = max(0.0, nueva.oferta[i] * factor)
        elif ajuste.tipo == CAPACIDAD and ajuste.objetivo in nueva.codigos_acopios:
            # Cuello de botella o cierre de un centro de acopio (HU-17)
            t = nueva.codigos_acopios.index(ajuste.objetivo)
            nueva.capacidad_acopios[t] = max(0.0, nueva.capacidad_acopios[t] * factor)
        elif ajuste.tipo == CAPACIDAD:
            for j in _columnas(nueva, ajuste.objetivo):
                nueva.capacidad[j] = max(0.0, nueva.capacidad[j] * factor)
        elif ajuste.tipo == COSTO_RUTA:
            i, j = _ruta(nueva, ajuste.objetivo)
            nueva.costos[i, j] = nueva.costos[i, j] * factor
        elif ajuste.tipo == CERRAR_RUTA:
            i, j = _ruta(nueva, ajuste.objetivo)
            nueva.rutas_habilitadas[i, j] = False
            nueva.costos[i, j] = 0.0
        else:
            raise ValueError(f"Tipo de ajuste desconocido: {ajuste.tipo}")
    return nueva


# Red lista para resolver: agrega la planta ficticia si el escenario la necesita
def balancear(red: RedLogistica, penalizacion: float) -> RedLogistica:
    validacion = ValidadorRed(penalizacion).validar(red)
    return preparar_red_para_motor(red, validacion)


# ---------- Rangos de estabilidad (re-optimización paramétrica) ----------


def _soporte(flujos: np.ndarray) -> np.ndarray:
    return flujos > TOLERANCIA_FLUJO


def _buscar_limite(
    valor: float, sigue_igual, direccion: int, minimo: float | None = 0.0
) -> float | None:
    """Mayor desplazamiento en `direccion` (+1 o -1) que no cambia la base óptima.

    Devuelve el valor límite, o None si no hay límite (infinito) dentro de la búsqueda.
    """
    paso = max(1.0, abs(valor) * 0.01)
    bueno = 0.0
    tope = max(abs(valor) * 50, 1e6)
    malo = None
    while paso <= tope:
        candidato = valor + direccion * paso
        if minimo is not None and candidato < minimo:
            candidato = minimo
            if sigue_igual(candidato):
                return minimo
            malo = abs(candidato - valor)
            break
        if sigue_igual(candidato):
            bueno = paso
            paso *= 2
        else:
            malo = paso
            break
    if malo is None:
        return None
    for _ in range(ITERACIONES_BISECCION):
        medio = (bueno + malo) / 2
        if sigue_igual(valor + direccion * medio):
            bueno = medio
        else:
            malo = medio
    return valor + direccion * bueno


@dataclass
class Rango:
    valor: float
    inferior: float | None
    superior: float | None


@dataclass
class RangosEstabilidad:
    costos: dict[tuple[int, int], Rango]
    capacidades: dict[int, Rango]
    ofertas: dict[int, Rango]
    omitido: str | None = None


def calcular_rangos(red: RedLogistica) -> RangosEstabilidad:
    """Rangos de costos unitarios (base óptima fija) y de capacidad/oferta (duales fijos)."""
    if int(red.rutas_habilitadas.sum()) > MAX_VARIABLES_RANGOS:
        return RangosEstabilidad({}, {}, {}, omitido="Red demasiado grande para calcular rangos")
    base = resolver_lp(red)
    if base is None:
        return RangosEstabilidad({}, {}, {}, omitido="La red base no tiene solución factible")
    soporte_base = _soporte(base.flujos)

    costos: dict[tuple[int, int], Rango] = {}
    for i in range(red.numero_empresas()):
        for j in range(red.numero_plantas()):
            if not red.rutas_habilitadas[i, j]:
                continue
            original = float(red.costos[i, j])

            def misma_base(valor: float, i: int = i, j: int = j) -> bool:
                prueba = copiar_red(red)
                prueba.costos[i, j] = valor
                solucion = resolver_lp(prueba)
                return solucion is not None and np.array_equal(
                    _soporte(solucion.flujos), soporte_base
                )

            inferior = _buscar_limite(original, misma_base, -1, minimo=0.0)
            if soporte_base[i, j]:
                superior = _buscar_limite(original, misma_base, +1, minimo=None)
            else:
                superior = None
            costos[(i, j)] = Rango(original, inferior, superior)

    def mismos_duales(prueba: RedLogistica) -> bool:
        solucion = resolver_lp(prueba)
        if solucion is None:
            return False
        return np.allclose(
            solucion.duales_capacidad, base.duales_capacidad, atol=TOLERANCIA_DUAL
        ) and np.allclose(solucion.duales_oferta, base.duales_oferta, atol=TOLERANCIA_DUAL)

    capacidades: dict[int, Rango] = {}
    for j in range(red.numero_plantas()):
        original = float(red.capacidad[j])

        def con_capacidad(valor: float, j: int = j) -> bool:
            prueba = copiar_red(red)
            prueba.capacidad[j] = valor
            return mismos_duales(prueba)

        capacidades[j] = Rango(
            original,
            _buscar_limite(original, con_capacidad, -1, minimo=0.0),
            _buscar_limite(original, con_capacidad, +1, minimo=None),
        )

    ofertas: dict[int, Rango] = {}
    for i in range(red.numero_empresas()):
        original = float(red.oferta[i])

        def con_oferta(valor: float, i: int = i) -> bool:
            prueba = copiar_red(red)
            prueba.oferta[i] = valor
            return mismos_duales(prueba)

        ofertas[i] = Rango(
            original,
            _buscar_limite(original, con_oferta, -1, minimo=0.0),
            _buscar_limite(original, con_oferta, +1, minimo=None),
        )

    return RangosEstabilidad(costos, capacidades, ofertas)


# Impacto en Z de variar cada parámetro ±porcentaje (gráfica de tornado)
@dataclass
class ImpactoTornado:
    parametro: str
    costo_menos: float | None
    costo_mas: float | None


def tornado(red: RedLogistica, porcentaje: float, penalizacion: float) -> list[ImpactoTornado]:
    candidatos: list[tuple[str, Ajuste, Ajuste]] = [
        (
            "Costo de transporte (k)",
            Ajuste(COSTO_TRANSPORTE, -porcentaje),
            Ajuste(COSTO_TRANSPORTE, porcentaje),
        ),
        ("Oferta total", Ajuste(OFERTA, -porcentaje), Ajuste(OFERTA, porcentaje)),
    ]
    for codigo in red.codigos_plantas:
        candidatos.append(
            (
                f"Capacidad {codigo}",
                Ajuste(CAPACIDAD, -porcentaje, codigo),
                Ajuste(CAPACIDAD, porcentaje, codigo),
            )
        )
    for codigo in red.codigos_empresas:
        candidatos.append(
            (
                f"Oferta {codigo}",
                Ajuste(OFERTA, -porcentaje, codigo),
                Ajuste(OFERTA, porcentaje, codigo),
            )
        )

    impactos = []
    for nombre, menos, mas in candidatos:
        valores = []
        for ajuste in (menos, mas):
            solucion = resolver_lp(balancear(aplicar_ajustes(red, [ajuste]), penalizacion))
            valores.append(None if solucion is None else solucion.costo)
        impactos.append(ImpactoTornado(nombre, valores[0], valores[1]))
    return impactos
