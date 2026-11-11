import time

import numpy as np

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

    inicializador = InicializadorAG(red.oferta, red.capacidad, red.costos, semilla, habilitadas)
    evaluador = EvaluadorAG(
        red.oferta, red.capacidad, red.costos, parametros.lambda_pen, habilitadas
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
    return ResultadoGenetico(
        costo_total=float(mejor.costo_total),
        flujos=np.array(mejor.cromosoma, dtype=float),
        violaciones=float(mejor.violaciones),
        convergencia=convergencia,
        tiempo_ms=tiempo_ms,
    )
