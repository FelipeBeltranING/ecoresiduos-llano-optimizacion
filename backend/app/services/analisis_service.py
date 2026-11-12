import statistics
import time
import uuid
from dataclasses import replace
from datetime import datetime

import numpy as np
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from app.db.models import Ejecucion, Escenario, Metodo
from app.db.models.analisis import (
    ESTADO_EN_CURSO,
    ESTADO_ERROR,
    ESTADO_TERMINADO,
    TIPO_COMPARACION,
    TIPO_ESCALABILIDAD,
    Analisis,
)
from app.optimizacion import contratos
from app.optimizacion.contratos import ParametrosAG
from app.optimizacion.instancias import generar_instancia
from app.optimizacion.red import RedLogistica
from app.optimizacion.sensibilidad.analizador import Ajuste, aplicar_ajustes, balancear
from app.optimizacion.verificador import verificar_solucion
from app.repositories import parametro_repository
from app.schemas.analisis import (
    AnalisisResumen,
    AnalisisSalida,
    ComparacionEntrada,
    EjecucionResumen,
    EscalabilidadEntrada,
    PaginaEjecuciones,
)
from app.services import ejecucion_service
from app.services.red_builder import RedBuilder


class AnalisisNoEncontradoError(Exception):
    pass


def _gap(costo: float, optimo: float) -> float:
    return 0.0 if optimo == 0 else (costo - optimo) / optimo * 100


# ---------- Registro y consulta de análisis ----------


def crear_registro(
    sesion: Session, tipo: str, parametros: dict, escenario_id: uuid.UUID | None = None
) -> Analisis:
    analisis = Analisis(
        tipo=tipo, estado=ESTADO_EN_CURSO, parametros=parametros, escenario_id=escenario_id
    )
    sesion.add(analisis)
    sesion.commit()
    sesion.refresh(analisis)
    return analisis


def a_salida(analisis: Analisis) -> AnalisisSalida:
    return AnalisisSalida(
        id=analisis.id,
        tipo=analisis.tipo,
        estado=analisis.estado,
        escenario_id=analisis.escenario_id,
        parametros=analisis.parametros,
        resultado=analisis.resultado,
        creado_en=analisis.creado_en,
    )


def obtener(sesion: Session, analisis_id: uuid.UUID) -> AnalisisSalida:
    analisis = sesion.get(Analisis, analisis_id)
    if analisis is None:
        raise AnalisisNoEncontradoError(f"No existe el análisis {analisis_id}")
    sesion.refresh(analisis)
    return a_salida(analisis)


def listar(sesion: Session, tipo: str | None = None, limite: int = 50) -> list[AnalisisResumen]:
    consulta = select(Analisis).order_by(Analisis.creado_en.desc()).limit(limite)
    if tipo:
        consulta = consulta.where(Analisis.tipo == tipo)
    return [
        AnalisisResumen(
            id=a.id,
            tipo=a.tipo,
            estado=a.estado,
            escenario_id=a.escenario_id,
            creado_en=a.creado_en,
        )
        for a in sesion.execute(consulta).scalars()
    ]


def _terminar(motor: Engine, analisis_id: uuid.UUID, estado: str, resultado: dict) -> None:
    with Session(bind=motor) as sesion:
        analisis = sesion.get(Analisis, analisis_id)
        analisis.estado = estado
        analisis.resultado = resultado
        sesion.commit()


# ---------- Comparativo exacto vs. AG (HU-13) ----------


def red_para_comparar(sesion: Session, escenario_id: uuid.UUID | None):
    if escenario_id is None:
        return ejecucion_service.preparar_red(sesion)
    escenario = sesion.get(Escenario, escenario_id)
    if escenario is None:
        raise AnalisisNoEncontradoError(f"No existe el escenario {escenario_id}")
    penalizacion = parametro_repository.obtener_valor(sesion, "penalizacion_ficticia")
    red = RedBuilder(sesion).construir()
    return balancear(aplicar_ajustes(red, [Ajuste(**a) for a in escenario.ajustes]), penalizacion)


# Escenarios a comparar: el campo singular se conserva por compatibilidad
def ids_de_escenarios(datos: ComparacionEntrada) -> list[uuid.UUID]:
    ids: list[uuid.UUID] = []
    if datos.escenario_id is not None:
        ids.append(datos.escenario_id)
    ids.extend(escenario for escenario in datos.escenarios if escenario not in ids)
    return ids


# Porcentaje de toneladas que cambian de planta frente a la red base
def cambio_de_asignacion(flujos_base: np.ndarray, flujos: np.ndarray) -> float:
    base = np.asarray(flujos_base, dtype=float)
    actual = np.asarray(flujos, dtype=float)
    total = float(np.abs(base).sum() + np.abs(actual).sum())
    if total <= 0:
        return 0.0
    return float(np.abs(base - actual).sum()) / total * 100


# Exacto + N corridas del AG sobre una red; devuelve el bloque del reporte
def evaluar_red(
    sesion: Session,
    red: RedLogistica,
    escenario_id: uuid.UUID | None,
    parametros: ParametrosAG,
    corridas: int,
) -> dict:
    solucion = contratos.resolver_exacto(red)
    exacto = ejecucion_service.ejecutar_exacto(sesion, red, escenario_id, solucion)
    optimo = float(solucion.costo_total)
    semilla_base = parametros.semilla or 0

    corridas_ag = []
    mejor = None
    for k in range(corridas):
        resultado = contratos.ejecutar_genetico(red, replace(parametros, semilla=semilla_base + k))
        corridas_ag.append(
            {
                "semilla": semilla_base + k,
                "costo": resultado.costo_total,
                "tiempo_ms": resultado.tiempo_ms,
                "violaciones": ejecucion_service.violaciones_de(red, resultado),
                "generaciones": len(resultado.convergencia),
                "gap": _gap(resultado.costo_total, optimo),
            }
        )
        if mejor is None or resultado.costo_total < mejor[1].costo_total:
            mejor = (semilla_base + k, resultado)

    mejor_ejecucion = ejecucion_service.guardar_genetico(
        sesion, red, replace(parametros, semilla=mejor[0]), mejor[1], escenario_id
    )
    costos = [c["costo"] for c in corridas_ag]
    tiempos = [c["tiempo_ms"] for c in corridas_ag]
    return {
        "exacto": {
            "ejecucion_id": str(exacto.id),
            "costo": optimo,
            "tiempo_ms": float(exacto.tiempo_ms),
            "violaciones": float(exacto.violaciones or 0),
            "estado": exacto.estado,
        },
        "ag": {
            "mejor_ejecucion_id": str(mejor_ejecucion.id),
            "mejor": min(costos),
            "peor": max(costos),
            "promedio": statistics.fmean(costos),
            "desviacion": statistics.pstdev(costos),
            "gap_mejor": _gap(min(costos), optimo),
            "gap_promedio": _gap(statistics.fmean(costos), optimo),
            "tiempo_promedio_ms": statistics.fmean(tiempos),
            "violaciones_max": max(c["violaciones"] for c in corridas_ag),
            "corridas": corridas_ag,
            "convergencia_mejor": [
                {
                    "generacion": r.generacion,
                    "mejor": r.mejor_costo,
                    "promedio": r.costo_promedio,
                }
                for r in mejor[1].convergencia
            ],
        },
        "flujos": solucion.flujos,
    }


# Una fila del reporte comparativo por escenario (HU-13)
def fila_comparacion(
    escenario_id: uuid.UUID | None,
    nombre: str,
    evaluacion: dict,
    flujos_base: np.ndarray | None,
) -> dict:
    optimo = evaluacion["exacto"]["costo"]
    mejor = evaluacion["ag"]["mejor"]
    return {
        "escenario_id": None if escenario_id is None else str(escenario_id),
        "nombre": nombre,
        "z_exacto": optimo,
        "z_ag": mejor,
        "gap": _gap(mejor, optimo),
        "tiempo_exacto_ms": evaluacion["exacto"]["tiempo_ms"],
        "tiempo_ag_ms": evaluacion["ag"]["tiempo_promedio_ms"],
        "cambio_asignacion": (
            0.0 if flujos_base is None else cambio_de_asignacion(flujos_base, evaluacion["flujos"])
        ),
    }


def ejecutar_comparacion(motor: Engine, analisis_id: uuid.UUID, entrada: dict) -> None:
    datos = ComparacionEntrada(**entrada)
    try:
        with Session(bind=motor) as sesion:
            parametros = ejecucion_service.convertir_parametros_ag(sesion, datos.parametros_ag)
            red_base = ejecucion_service.preparar_red(sesion)
            base = evaluar_red(sesion, red_base, None, parametros, datos.corridas)
            filas = [fila_comparacion(None, "Caso base", base, None)]

            evaluados: dict[uuid.UUID, dict] = {}
            for escenario_id in ids_de_escenarios(datos):
                escenario = sesion.get(Escenario, escenario_id)
                if escenario is None:
                    raise AnalisisNoEncontradoError(f"No existe el escenario {escenario_id}")
                evaluacion = evaluar_red(
                    sesion,
                    red_para_comparar(sesion, escenario_id),
                    escenario_id,
                    parametros,
                    datos.corridas,
                )
                evaluados[escenario_id] = evaluacion
                filas.append(
                    fila_comparacion(escenario_id, escenario.nombre, evaluacion, base["flujos"])
                )

            # Con un único escenario el reporte principal sigue siendo ese escenario
            principal = base
            if datos.escenario_id is not None and not datos.escenarios:
                principal = evaluados[datos.escenario_id]

            resultado = {
                "exacto": principal["exacto"],
                "ag": principal["ag"],
                "red": {
                    "empresas": red_base.numero_empresas(),
                    "plantas": red_base.numero_plantas(),
                    "acopios": red_base.numero_acopios(),
                    "usa_planta_ficticia": red_base.tiene_planta_ficticia(),
                },
                "filas": filas,
            }
        _terminar(motor, analisis_id, ESTADO_TERMINADO, resultado)
    except Exception as error:  # noqa: BLE001 - el error se guarda para la interfaz
        _terminar(motor, analisis_id, ESTADO_ERROR, {"error": str(error)})


# ---------- Escalabilidad (HU-14) ----------


def ejecutar_escalabilidad(motor: Engine, analisis_id: uuid.UUID, entrada: dict) -> None:
    datos = EscalabilidadEntrada(**entrada)
    try:
        with Session(bind=motor) as sesion:
            parametros = ejecucion_service.convertir_parametros_ag(sesion, datos.parametros_ag)
        filas = []
        for tamano in datos.tamanos:
            red = generar_instancia(tamano.empresas, tamano.plantas, datos.semilla)
            inicio = time.perf_counter()
            exacto = contratos.resolver_exacto(red)
            tiempo_exacto = (time.perf_counter() - inicio) * 1000
            genetico = contratos.ejecutar_genetico(red, parametros)
            filas.append(
                {
                    "empresas": tamano.empresas,
                    "plantas": tamano.plantas,
                    "variables": tamano.empresas * tamano.plantas,
                    "costo_exacto": exacto.costo_total,
                    "tiempo_exacto_ms": tiempo_exacto,
                    "costo_ag": genetico.costo_total,
                    "tiempo_ag_ms": genetico.tiempo_ms,
                    "gap": _gap(genetico.costo_total, exacto.costo_total),
                    "violaciones_ag": verificar_solucion(red, genetico.flujos).total,
                    "generaciones_ag": len(genetico.convergencia),
                }
            )
        _terminar(motor, analisis_id, ESTADO_TERMINADO, {"filas": filas})
    except Exception as error:  # noqa: BLE001
        _terminar(motor, analisis_id, ESTADO_ERROR, {"error": str(error)})


def iniciar(
    sesion: Session, tipo: str, entrada: ComparacionEntrada | EscalabilidadEntrada
) -> Analisis:
    ids = ids_de_escenarios(entrada) if isinstance(entrada, ComparacionEntrada) else []
    for escenario_id in ids:
        if sesion.get(Escenario, escenario_id) is None:
            raise AnalisisNoEncontradoError(f"No existe el escenario {escenario_id}")
    if tipo == TIPO_COMPARACION:
        ejecucion_service.preparar_red(sesion)
    # El registro guarda un escenario solo cuando la comparación es de uno
    return crear_registro(
        sesion, tipo, entrada.model_dump(mode="json"), ids[0] if len(ids) == 1 else None
    )


TAREAS = {TIPO_COMPARACION: ejecutar_comparacion, TIPO_ESCALABILIDAD: ejecutar_escalabilidad}


# ---------- Historial de ejecuciones (HU-15) ----------


def historial(
    sesion: Session,
    metodo: Metodo | None,
    escenario_id: uuid.UUID | None,
    solo_base: bool,
    desde: datetime | None,
    hasta: datetime | None,
    pagina: int,
    tamano: int,
) -> PaginaEjecuciones:
    condiciones = []
    if metodo is not None:
        condiciones.append(Ejecucion.metodo == metodo)
    if escenario_id is not None:
        condiciones.append(Ejecucion.escenario_id == escenario_id)
    if solo_base:
        condiciones.append(Ejecucion.escenario_id.is_(None))
    if desde is not None:
        condiciones.append(Ejecucion.creado_en >= desde)
    if hasta is not None:
        condiciones.append(Ejecucion.creado_en <= hasta)

    total = sesion.execute(
        select(func.count()).select_from(Ejecucion).where(*condiciones)
    ).scalar_one()
    consulta = (
        select(Ejecucion, Escenario.nombre)
        .outerjoin(Escenario, Ejecucion.escenario_id == Escenario.id)
        .where(*condiciones)
        .order_by(Ejecucion.creado_en.desc())
        .offset((pagina - 1) * tamano)
        .limit(tamano)
    )
    items = []
    for ejecucion, nombre in sesion.execute(consulta):
        items.append(
            EjecucionResumen(
                id=ejecucion.id,
                metodo=ejecucion.metodo,
                estado=ejecucion.estado,
                costo_total=None if ejecucion.costo_total is None else float(ejecucion.costo_total),
                tiempo_ms=None if ejecucion.tiempo_ms is None else float(ejecucion.tiempo_ms),
                violaciones=None if ejecucion.violaciones is None else float(ejecucion.violaciones),
                escenario_id=ejecucion.escenario_id,
                escenario_nombre=nombre,
                creado_en=ejecucion.creado_en,
            )
        )
    return PaginaEjecuciones(total=total, pagina=pagina, tamano=tamano, items=items)
