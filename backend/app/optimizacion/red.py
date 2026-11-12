from dataclasses import dataclass, field, fields, replace

import numpy as np

CODIGO_PLANTA_FICTICIA = "FICTICIA"


# Datos de entrada para construir la red
@dataclass
class DatosEmpresa:
    codigo: str
    oferta: float


@dataclass
class DatosPlanta:
    codigo: str
    capacidad: float
    costo_operacion: float


# Centro de acopio: nodo de paso con capacidad y costo de manejo por tonelada (HU-17)
@dataclass
class DatosAcopio:
    codigo: str
    capacidad: float
    costo_manejo: float = 0.0


@dataclass
class DatosRuta:
    origen: str
    destino: str
    distancia_km: float | None
    costo_km_t: float | None
    habilitada: bool


# Red logística en forma de vectores y matrices
@dataclass
class RedLogistica:
    codigos_empresas: list[str]
    codigos_plantas: list[str]
    oferta: np.ndarray
    capacidad: np.ndarray
    costos: np.ndarray
    rutas_habilitadas: np.ndarray
    # Costo de operación por planta (o_j); permite separar el componente de transporte
    costo_operacion: np.ndarray | None = None
    # Centros de acopio (HU-17): arcos empresa → acopio y acopio → planta
    codigos_acopios: list[str] = field(default_factory=list)
    capacidad_acopios: np.ndarray | None = None
    # Costo de manejo por acopio (h_t); ya está sumado en costos_a_acopio
    costo_manejo: np.ndarray | None = None
    costos_a_acopio: np.ndarray | None = None
    rutas_a_acopio: np.ndarray | None = None
    costos_desde_acopio: np.ndarray | None = None
    rutas_desde_acopio: np.ndarray | None = None

    def numero_acopios(self) -> int:
        return len(self.codigos_acopios)

    def tiene_acopios(self) -> bool:
        return self.numero_acopios() > 0

    def numero_empresas(self) -> int:
        return len(self.codigos_empresas)

    def numero_plantas(self) -> int:
        return len(self.codigos_plantas)

    def costo(self, codigo_empresa: str, codigo_planta: str) -> float:
        fila = self.codigos_empresas.index(codigo_empresa)
        columna = self.codigos_plantas.index(codigo_planta)
        return float(self.costos[fila, columna])

    def tiene_planta_ficticia(self) -> bool:
        return CODIGO_PLANTA_FICTICIA in self.codigos_plantas


# Costo unitario de una ruta: c_ij = k_ij * d_ij + o_j
def calcular_costo_unitario(
    distancia_km: float, costo_km_ruta: float | None, costo_km_global: float, costo_operacion: float
) -> float:
    costo_km = costo_km_global
    if costo_km_ruta is not None:
        costo_km = costo_km_ruta
    return costo_km * distancia_km + costo_operacion


# Construcción de la red a partir de los datos de empresas, plantas y rutas
def construir_red(
    empresas: list[DatosEmpresa],
    plantas: list[DatosPlanta],
    rutas: list[DatosRuta],
    costo_km_global: float,
    acopios: list[DatosAcopio] | None = None,
) -> RedLogistica:
    codigos_empresas = []
    oferta = []
    for empresa in empresas:
        codigos_empresas.append(empresa.codigo)
        oferta.append(empresa.oferta)

    codigos_plantas = []
    capacidad = []
    costo_operacion = {}
    for planta in plantas:
        codigos_plantas.append(planta.codigo)
        capacidad.append(planta.capacidad)
        costo_operacion[planta.codigo] = planta.costo_operacion

    m = len(codigos_empresas)
    n = len(codigos_plantas)
    costos = np.zeros((m, n))
    rutas_habilitadas = np.zeros((m, n), dtype=bool)

    for ruta in rutas:
        if ruta.origen not in codigos_empresas or ruta.destino not in codigos_plantas:
            continue
        if not ruta.habilitada or ruta.distancia_km is None:
            continue
        fila = codigos_empresas.index(ruta.origen)
        columna = codigos_plantas.index(ruta.destino)
        costos[fila, columna] = calcular_costo_unitario(
            ruta.distancia_km, ruta.costo_km_t, costo_km_global, costo_operacion[ruta.destino]
        )
        rutas_habilitadas[fila, columna] = True

    red = RedLogistica(
        codigos_empresas=codigos_empresas,
        codigos_plantas=codigos_plantas,
        oferta=np.array(oferta, dtype=float),
        capacidad=np.array(capacidad, dtype=float),
        costos=costos,
        rutas_habilitadas=rutas_habilitadas,
        costo_operacion=np.array([costo_operacion[c] for c in codigos_plantas], dtype=float),
    )
    if acopios:
        agregar_acopios(red, acopios, rutas, costo_km_global)
    return red


# Arcos empresa → acopio (transporte + manejo) y acopio → planta (transporte + operación)
def agregar_acopios(
    red: RedLogistica, acopios: list[DatosAcopio], rutas: list[DatosRuta], costo_km_global: float
) -> None:
    codigos = [acopio.codigo for acopio in acopios]
    manejo = np.array([acopio.costo_manejo for acopio in acopios], dtype=float)
    m, n, t = red.numero_empresas(), red.numero_plantas(), len(codigos)

    red.codigos_acopios = codigos
    red.capacidad_acopios = np.array([acopio.capacidad for acopio in acopios], dtype=float)
    red.costo_manejo = manejo
    red.costos_a_acopio = np.zeros((m, t))
    red.rutas_a_acopio = np.zeros((m, t), dtype=bool)
    red.costos_desde_acopio = np.zeros((t, n))
    red.rutas_desde_acopio = np.zeros((t, n), dtype=bool)

    for ruta in rutas:
        if not ruta.habilitada or ruta.distancia_km is None:
            continue
        if ruta.origen in red.codigos_empresas and ruta.destino in codigos:
            fila = red.codigos_empresas.index(ruta.origen)
            columna = codigos.index(ruta.destino)
            red.costos_a_acopio[fila, columna] = calcular_costo_unitario(
                ruta.distancia_km, ruta.costo_km_t, costo_km_global, manejo[columna]
            )
            red.rutas_a_acopio[fila, columna] = True
        elif ruta.origen in codigos and ruta.destino in red.codigos_plantas:
            fila = codigos.index(ruta.origen)
            columna = red.codigos_plantas.index(ruta.destino)
            red.costos_desde_acopio[fila, columna] = calcular_costo_unitario(
                ruta.distancia_km, ruta.costo_km_t, costo_km_global, red.costo_operacion[columna]
            )
            red.rutas_desde_acopio[fila, columna] = True


# Copia independiente de la red (los arreglos no se comparten)
def copiar_red(red: RedLogistica) -> RedLogistica:
    cambios = {}
    for campo in fields(red):
        valor = getattr(red, campo.name)
        if isinstance(valor, np.ndarray):
            cambios[campo.name] = valor.copy()
        elif isinstance(valor, list):
            cambios[campo.name] = list(valor)
    return replace(red, **cambios)


# Red con una planta ficticia que recibe el residuo que no cabe en las plantas reales
def agregar_planta_ficticia(
    red: RedLogistica, capacidad_ficticia: float, penalizacion: float
) -> RedLogistica:
    m = red.numero_empresas()

    nueva = copiar_red(red)
    nueva.codigos_plantas.append(CODIGO_PLANTA_FICTICIA)
    nueva.capacidad = np.append(red.capacidad, capacidad_ficticia)
    nueva.costos = np.hstack([red.costos, np.full((m, 1), penalizacion)])
    nueva.rutas_habilitadas = np.hstack([red.rutas_habilitadas, np.ones((m, 1), dtype=bool)])
    if red.costo_operacion is not None:
        nueva.costo_operacion = np.append(red.costo_operacion, penalizacion)
    if red.tiene_acopios():
        # Los acopios no envían a la planta ficticia
        t = red.numero_acopios()
        nueva.costos_desde_acopio = np.hstack([red.costos_desde_acopio, np.zeros((t, 1))])
        nueva.rutas_desde_acopio = np.hstack(
            [red.rutas_desde_acopio, np.zeros((t, 1), dtype=bool)]
        )
    return nueva


# Resultado de validar la red
@dataclass
class ResultadoValidacion:
    oferta_total: float
    capacidad_total: float
    holgura_capacidad: float
    necesita_planta_ficticia: bool
    capacidad_ficticia: float
    costo_ficticia: float
    nodos_aislados: list[str] = field(default_factory=list)
    mensajes: list[str] = field(default_factory=list)

    def es_valida(self) -> bool:
        return len(self.nodos_aislados) == 0


# Validación del balance y de la consistencia de la red (HU-06)
class ValidadorRed:
    def __init__(self, penalizacion_ficticia: float) -> None:
        self.penalizacion_ficticia = penalizacion_ficticia

    def buscar_nodos_aislados(self, red: RedLogistica) -> list[str]:
        aislados = []
        for fila, codigo in enumerate(red.codigos_empresas):
            tiene_ruta_directa = red.rutas_habilitadas[fila, :].any()
            if not tiene_ruta_directa and not self.llega_por_acopio(red, fila):
                aislados.append(codigo)
        return aislados

    # ¿La empresa llega a alguna planta pasando por un acopio?
    def llega_por_acopio(self, red: RedLogistica, fila: int) -> bool:
        for acopio in range(red.numero_acopios()):
            if red.rutas_a_acopio[fila, acopio] and red.rutas_desde_acopio[acopio, :].any():
                return True
        return False

    def validar(self, red: RedLogistica) -> ResultadoValidacion:
        oferta_total = float(red.oferta.sum())
        capacidad_total = float(red.capacidad.sum())
        diferencia = oferta_total - capacidad_total

        resultado = ResultadoValidacion(
            oferta_total=oferta_total,
            capacidad_total=capacidad_total,
            holgura_capacidad=max(0.0, -diferencia),
            necesita_planta_ficticia=diferencia > 0,
            capacidad_ficticia=max(0.0, diferencia),
            costo_ficticia=self.penalizacion_ficticia,
        )

        if resultado.necesita_planta_ficticia:
            resultado.mensajes.append(
                f"La oferta supera la capacidad en {diferencia:g} t: se agregará una planta "
                f"ficticia con esa capacidad y costo {self.penalizacion_ficticia:g} COP/t."
            )
        else:
            holgura = resultado.holgura_capacidad
            resultado.mensajes.append(
                f"La capacidad cubre la oferta con una holgura de {holgura:g} t."
            )

        resultado.nodos_aislados = self.buscar_nodos_aislados(red)
        for codigo in resultado.nodos_aislados:
            resultado.mensajes.append(
                f"Nodo aislado: la empresa {codigo} no tiene rutas habilitadas."
            )

        return resultado


# Red lista para los motores: agrega la planta ficticia solo si hace falta
def preparar_red_para_motor(red: RedLogistica, validacion: ResultadoValidacion) -> RedLogistica:
    if not validacion.necesita_planta_ficticia:
        return red
    return agregar_planta_ficticia(red, validacion.capacidad_ficticia, validacion.costo_ficticia)
