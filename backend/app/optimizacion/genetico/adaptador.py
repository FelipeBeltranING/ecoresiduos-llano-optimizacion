import time

import numpy as np

from app.optimizacion.caminos import caminos_a_arcos, construir_caminos
from app.optimizacion.contratos import ParametrosAG, RegistroConvergencia, ResultadoGenetico
from app.optimizacion.genetico.algoritmo import (
    EvaluadorAG,
    InicializadorAG,
    MotorAG,
    OperadoresGeneticos,
)
from app.optimizacion.red import RedLogistica


# Ejecuta el AG del equipo sobre una RedLogistica y devuelve el contrato ResultadoGenetico
def ejecutar(red: RedLogistica, parametros: ParametrosAG) -> ResultadoGenetico:
    inicio = time.perf_counter()
    semilla = parametros.semilla
    habilitadas = red.rutas_habilitadas
    costos, capacidad, recursos = red.costos, red.capacidad, None
    if red.tiene_acopios():
        # Cromosoma empresa × camino (directo o pasando por un acopio), HU-17
        caminos = construir_caminos(red)
        costos, habilitadas = caminos.costos, caminos.habilitadas
        capacidad, recursos = caminos.capacidad_recursos, caminos.recursos

    inicializador = InicializadorAG(red.oferta, capacidad, costos, semilla, habilitadas, recursos)
    evaluador = EvaluadorAG(
        red.oferta, capacidad, costos, parametros.lambda_pen, habilitadas, recursos
    )
    # Semilla distinta para los operadores, pero derivada de la misma (reproducible)
    semilla_operadores = None if semilla is None else semilla + 1
    operadores = OperadoresGeneticos(semilla_operadores, habilitadas)

    motor = MotorAG(inicializador, evaluador, operadores)
    mejor = motor.ejecutar(
        tam_poblacion=parametros.tamano_poblacion,
        generaciones=parametros.generaciones,
        tasa_cruce=parametros.prob_cruce,
        tasa_mutacion=parametros.prob_mutacion,
        tipo_seleccion=parametros.tipo_seleccion,
        tipo_cruce=parametros.tipo_cruce,
        elitismo=parametros.elitismo,
    )
    tiempo_ms = (time.perf_counter() - inicio) * 1000

    convergencia = [
        RegistroConvergencia(generacion=g, mejor_costo=mejor_costo, costo_promedio=promedio)
        for g, mejor_costo, promedio in motor.historial
    ]
    arcos = caminos_a_arcos(red, np.array(mejor.cromosoma, dtype=float))
    return ResultadoGenetico(
        costo_total=float(mejor.costo_total),
        flujos=arcos.directos,
        violaciones=float(mejor.violaciones),
        convergencia=convergencia,
        tiempo_ms=tiempo_ms,
        flujos_a_acopio=arcos.a_acopio,
        flujos_desde_acopio=arcos.desde_acopio,
    )
