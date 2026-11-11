from dataclasses import dataclass, field

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

    return RedLogistica(
        codigos_empresas=codigos_empresas,
        codigos_plantas=codigos_plantas,
        oferta=np.array(oferta, dtype=float),
        capacidad=np.array(capacidad, dtype=float),
        costos=costos,
        rutas_habilitadas=rutas_habilitadas,
    )


# Red con una planta ficticia que recibe el residuo que no cabe en las plantas reales
def agregar_planta_ficticia(
    red: RedLogistica, capacidad_ficticia: float, penalizacion: float
) -> RedLogistica:
    m = red.numero_empresas()

    columna_costos = np.full((m, 1), penalizacion)
    columna_habilitada = np.ones((m, 1), dtype=bool)

    codigos_plantas = list(red.codigos_plantas)
    codigos_plantas.append(CODIGO_PLANTA_FICTICIA)

    return RedLogistica(
        codigos_empresas=list(red.codigos_empresas),
        codigos_plantas=codigos_plantas,
        oferta=red.oferta.copy(),
        capacidad=np.append(red.capacidad, capacidad_ficticia),
        costos=np.hstack([red.costos, columna_costos]),
        rutas_habilitadas=np.hstack([red.rutas_habilitadas, columna_habilitada]),
    )


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
            rutas_de_la_empresa = red.rutas_habilitadas[fila, :]
            if not rutas_de_la_empresa.any():
                aislados.append(codigo)
        return aislados

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
