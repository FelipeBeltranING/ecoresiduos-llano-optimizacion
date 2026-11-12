from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Nodo
from app.optimizacion.criticidad import MECANISMOS, calcular_ice
from app.repositories import parametro_repository
from app.schemas.criticidad import CriticidadNodoSalida, CriticidadSalida
from app.services.ejecucion_service import RedNoValidaError
from app.services.red_builder import RedBuilder

REFERENCIA = (
    "L. A. Vega-Linares, D. F. Beltrán-Tabares, O. L. Vega-Márquez y N. E. Suat-Rojas, "
    '"Redes neuronales de grafos para resiliencia en microservicios," en Memorias del VI '
    "Congreso Internacional de Ciencias Básicas e Ingeniería - CICI 2026, Universidad de los "
    "Llanos, Villavicencio, 2026."
)


# ICE de las plantas y acopios de la red activa, con su impacto al fallar (HU-20)
def analizar(sesion: Session, alfa: float, beta: float, gamma: float) -> CriticidadSalida:
    constructor = RedBuilder(sesion)
    red = constructor.construir()
    validacion = constructor.crear_validador().validar(red)
    if not validacion.es_valida():
        raise RedNoValidaError(validacion.mensajes)
    penalizacion = parametro_repository.obtener_valor(sesion, "penalizacion_ficticia")
    analisis = calcular_ice(red, penalizacion, (alfa, beta, gamma))

    nombres = dict(sesion.execute(select(Nodo.codigo, Nodo.nombre)).all())
    por_impacto = sorted(analisis.nodos, key=lambda n: n.delta_costo_pct, reverse=True)
    nodos = [
        CriticidadNodoSalida(
            codigo=nodo.codigo,
            nombre=nombres.get(nodo.codigo),
            tipo=nodo.tipo,
            intermediacion=round(nodo.intermediacion, 4),
            grado_entrada=round(nodo.grado_entrada, 4),
            resiliencia=round(nodo.resiliencia, 4),
            mecanismos=dict(zip(MECANISMOS, nodo.mecanismos, strict=True)),
            ice=round(nodo.ice, 4),
            ranking_ice=posicion + 1,
            delta_costo_pct=round(nodo.delta_costo_pct, 2),
            toneladas_sin_planta=round(nodo.toneladas_sin_planta, 2),
            ranking_impacto=por_impacto.index(nodo) + 1,
        )
        for posicion, nodo in enumerate(analisis.nodos)
    ]
    calibrados = analisis.pesos_calibrados
    return CriticidadSalida(
        alfa=alfa,
        beta=beta,
        gamma=gamma,
        costo_base=analisis.costo_base,
        nodos=nodos,
        spearman=analisis.spearman,
        pesos_calibrados=None if calibrados is None else list(calibrados),
        spearman_calibrado=analisis.spearman_calibrado,
        notas=analisis.notas,
        referencia=REFERENCIA,
    )
