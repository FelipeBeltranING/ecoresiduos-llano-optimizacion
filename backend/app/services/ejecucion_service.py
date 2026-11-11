import uuid
from dataclasses import asdict

from sqlalchemy.orm import Session

from app.db.models import Ejecucion, Metodo
from app.db.models.sensibilidad_resultado import (
    COSTO_REDUCIDO,
    DUAL_CAPACIDAD,
    DUAL_OFERTA,
    HOLGURA_CAPACIDAD,
)
from app.optimizacion import contratos
from app.optimizacion.contratos import ParametrosAG, ResultadoExacto, ResultadoGenetico
from app.optimizacion.red import (
    CODIGO_PLANTA_FICTICIA,
    RedLogistica,
    ResultadoValidacion,
    preparar_red_para_motor,
)
from app.repositories import ejecucion_repository, parametro_repository
from app.schemas.optimizacion import (
    ConvergenciaSalida,
    EjecucionDetalle,
    FlujoSalida,
    ParametrosAGEntrada,
    SensibilidadSalida,
)
from app.services.red_builder import RedBuilder

UMBRAL_FLUJO = 1e-9
ESTADO_TERMINADA = "Terminada"


# Error cuando la red no se puede optimizar (por ejemplo, un nodo aislado)
class RedNoValidaError(Exception):
    def __init__(self, mensajes: list[str]) -> None:
        super().__init__("; ".join(mensajes))
        self.mensajes = mensajes


# Validación de la red armada desde la base
def validar_red(sesion: Session) -> ResultadoValidacion:
    constructor = RedBuilder(sesion)
    red = constructor.construir()
    return constructor.crear_validador().validar(red)


# Red lista para un motor: válida y balanceada con planta ficticia si hace falta
def preparar_red(sesion: Session) -> RedLogistica:
    constructor = RedBuilder(sesion)
    red = constructor.construir()
    validacion = constructor.crear_validador().validar(red)
    if not validacion.es_valida():
        raise RedNoValidaError(validacion.mensajes)
    return preparar_red_para_motor(red, validacion)


# Copia de la red en formato JSON para guardar con la ejecución
def snapshot_de_red(red: RedLogistica) -> dict:
    return {
        "empresas": red.codigos_empresas,
        "plantas": red.codigos_plantas,
        "oferta": red.oferta.tolist(),
        "capacidad": red.capacidad.tolist(),
        "costos": red.costos.tolist(),
        "rutas_habilitadas": red.rutas_habilitadas.tolist(),
    }


# Guardado de los flujos mayores que cero
def guardar_flujos(sesion: Session, ejecucion: Ejecucion, red: RedLogistica, flujos) -> None:
    ids_nodos = ejecucion_repository.mapa_ids_nodos(sesion)
    for i, codigo_empresa in enumerate(red.codigos_empresas):
        for j, codigo_planta in enumerate(red.codigos_plantas):
            toneladas = float(flujos[i, j])
            if toneladas <= UMBRAL_FLUJO:
                continue
            destino_id = None
            if codigo_planta != CODIGO_PLANTA_FICTICIA:
                destino_id = ids_nodos[codigo_planta]
            ejecucion_repository.agregar_flujo(
                sesion,
                ejecucion.id,
                ids_nodos[codigo_empresa],
                destino_id,
                toneladas,
                float(red.costos[i, j]),
            )


# Guardado de duales, holguras y costos reducidos del modelo exacto
def guardar_sensibilidad_exacto(
    sesion: Session, ejecucion: Ejecucion, red: RedLogistica, resultado: ResultadoExacto
) -> None:
    ids_nodos = ejecucion_repository.mapa_ids_nodos(sesion)
    ids_rutas = ejecucion_repository.mapa_ids_rutas(sesion)

    for i, codigo_empresa in enumerate(red.codigos_empresas):
        ejecucion_repository.agregar_sensibilidad(
            sesion,
            ejecucion.id,
            DUAL_OFERTA,
            float(resultado.duales_oferta[i]),
            nodo_id=ids_nodos[codigo_empresa],
        )

    for j, codigo_planta in enumerate(red.codigos_plantas):
        if codigo_planta == CODIGO_PLANTA_FICTICIA:
            continue
        nodo_id = ids_nodos[codigo_planta]
        dual = float(resultado.duales_capacidad[j])
        holgura = float(resultado.holguras[j])
        ejecucion_repository.agregar_sensibilidad(
            sesion, ejecucion.id, DUAL_CAPACIDAD, dual, nodo_id=nodo_id
        )
        ejecucion_repository.agregar_sensibilidad(
            sesion, ejecucion.id, HOLGURA_CAPACIDAD, holgura, nodo_id=nodo_id
        )

    for i, codigo_empresa in enumerate(red.codigos_empresas):
        for j, codigo_planta in enumerate(red.codigos_plantas):
            ruta_id = ids_rutas.get((codigo_empresa, codigo_planta))
            if ruta_id is None:
                continue
            ejecucion_repository.agregar_sensibilidad(
                sesion,
                ejecucion.id,
                COSTO_REDUCIDO,
                float(resultado.costos_reducidos[i, j]),
                ruta_id=ruta_id,
            )


# Ejecución del modelo exacto y guardado de su resultado
def ejecutar_exacto(sesion: Session) -> Ejecucion:
    red = preparar_red(sesion)
    resultado = contratos.resolver_exacto(red)

    try:
        ejecucion = ejecucion_repository.crear_ejecucion(
            sesion,
            Metodo.EXACTO,
            resultado.estado,
            resultado.costo_total,
            resultado.tiempo_ms,
            None,
            snapshot_de_red(red),
        )
        guardar_flujos(sesion, ejecucion, red, resultado.flujos)
        guardar_sensibilidad_exacto(sesion, ejecucion, red, resultado)
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    return ejecucion


# Parámetros del AG: lambda sale de parametro_global si no se envía
def convertir_parametros_ag(sesion: Session, entrada: ParametrosAGEntrada) -> ParametrosAG:
    lambda_pen = entrada.lambda_pen
    if lambda_pen is None:
        lambda_pen = parametro_repository.obtener_valor(sesion, "lambda_ag")
    return ParametrosAG(
        tamano_poblacion=entrada.tamano_poblacion,
        generaciones=entrada.generaciones,
        prob_cruce=entrada.prob_cruce,
        prob_mutacion=entrada.prob_mutacion,
        elitismo=entrada.elitismo,
        lambda_pen=lambda_pen,
        semilla=entrada.semilla,
    )


# Guardado de la convergencia del AG
def guardar_convergencia(
    sesion: Session, ejecucion: Ejecucion, resultado: ResultadoGenetico
) -> None:
    for registro in resultado.convergencia:
        ejecucion_repository.agregar_convergencia(
            sesion,
            ejecucion.id,
            registro.generacion,
            registro.mejor_costo,
            registro.costo_promedio,
        )


# Ejecución del AG y guardado de su resultado
def ejecutar_genetico(sesion: Session, entrada: ParametrosAGEntrada) -> Ejecucion:
    red = preparar_red(sesion)
    parametros = convertir_parametros_ag(sesion, entrada)
    resultado = contratos.ejecutar_genetico(red, parametros)

    try:
        ejecucion = ejecucion_repository.crear_ejecucion(
            sesion,
            Metodo.GENETICO,
            ESTADO_TERMINADA,
            resultado.costo_total,
            resultado.tiempo_ms,
            asdict(parametros),
            snapshot_de_red(red),
        )
        guardar_flujos(sesion, ejecucion, red, resultado.flujos)
        guardar_convergencia(sesion, ejecucion, resultado)
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    return ejecucion


# Detalle de una ejecución con flujos, sensibilidad y convergencia
def obtener_detalle(sesion: Session, ejecucion_id: uuid.UUID) -> EjecucionDetalle | None:
    ejecucion = ejecucion_repository.buscar_ejecucion(sesion, ejecucion_id)
    if ejecucion is None:
        return None

    flujos = []
    for origen, destino, toneladas, costo_unitario in ejecucion_repository.listar_flujos(
        sesion, ejecucion_id
    ):
        flujos.append(
            FlujoSalida(
                origen=origen, destino=destino, toneladas=toneladas, costo_unitario=costo_unitario
            )
        )

    sensibilidad = []
    for registro in ejecucion_repository.listar_sensibilidad(sesion, ejecucion_id):
        sensibilidad.append(SensibilidadSalida(**registro))

    convergencia = []
    for registro in ejecucion_repository.listar_convergencia(sesion, ejecucion_id):
        convergencia.append(
            ConvergenciaSalida(
                generacion=registro.generacion,
                mejor_costo=registro.mejor_costo,
                costo_promedio=registro.costo_promedio,
            )
        )

    return EjecucionDetalle(
        id=ejecucion.id,
        metodo=ejecucion.metodo,
        estado=ejecucion.estado,
        costo_total=ejecucion.costo_total,
        tiempo_ms=ejecucion.tiempo_ms,
        parametros=ejecucion.parametros,
        creado_en=ejecucion.creado_en,
        flujos=flujos,
        sensibilidad=sensibilidad,
        convergencia=convergencia,
    )
