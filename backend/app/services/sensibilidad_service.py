import uuid

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.db.models import Ejecucion, Escenario, Metodo, SensibilidadResultado
from app.db.models.sensibilidad_resultado import COSTO_REDUCIDO, DUAL_CAPACIDAD, DUAL_OFERTA
from app.optimizacion.red import CODIGO_PLANTA_FICTICIA
from app.optimizacion.sensibilidad.analizador import (
    Ajuste,
    aplicar_ajustes,
    balancear,
    calcular_rangos,
    resolver_lp,
    tornado,
)
from app.repositories import ejecucion_repository, parametro_repository
from app.schemas.sensibilidad import (
    CambioFlujo,
    EjecutarEscenarioEntrada,
    EscenarioEntrada,
    EscenarioSalida,
    ImpactoSalida,
    RangoSalida,
    RangosSalida,
    ResultadoEscenario,
    TornadoSalida,
)
from app.services import ejecucion_service
from app.services.ejecucion_service import RedNoValidaError
from app.services.red_builder import RedBuilder


class EscenarioNoEncontradoError(Exception):
    pass


class EscenarioInvalidoError(Exception):
    pass


def a_salida(escenario: Escenario) -> EscenarioSalida:
    return EscenarioSalida(
        id=escenario.id,
        nombre=escenario.nombre,
        descripcion=escenario.descripcion,
        ajustes=escenario.ajustes,
        creado_en=escenario.creado_en,
    )


# ---------- CRUD de escenarios (HU-11) ----------


def crear_escenario(sesion: Session, entrada: EscenarioEntrada) -> EscenarioSalida:
    red = RedBuilder(sesion).construir()
    try:
        aplicar_ajustes(red, [Ajuste(**a.model_dump()) for a in entrada.ajustes])
    except ValueError as error:
        raise EscenarioInvalidoError(str(error)) from error
    escenario = Escenario(
        nombre=entrada.nombre,
        descripcion=entrada.descripcion,
        ajustes=[a.model_dump() for a in entrada.ajustes],
    )
    sesion.add(escenario)
    sesion.commit()
    sesion.refresh(escenario)
    return a_salida(escenario)


def listar_escenarios(sesion: Session) -> list[EscenarioSalida]:
    consulta = select(Escenario).order_by(Escenario.creado_en.desc())
    return [a_salida(e) for e in sesion.execute(consulta).scalars()]


def buscar_escenario(sesion: Session, escenario_id: uuid.UUID) -> Escenario:
    escenario = sesion.get(Escenario, escenario_id)
    if escenario is None:
        raise EscenarioNoEncontradoError(f"No existe el escenario {escenario_id}")
    return escenario


def eliminar_escenario(sesion: Session, escenario_id: uuid.UUID) -> None:
    sesion.delete(buscar_escenario(sesion, escenario_id))
    sesion.commit()


# ---------- Ejecución del escenario con ambos métodos ----------


def ejecutar_escenario(
    sesion: Session, escenario_id: uuid.UUID, entrada: EjecutarEscenarioEntrada
) -> ResultadoEscenario:
    escenario = buscar_escenario(sesion, escenario_id)
    constructor = RedBuilder(sesion)
    red_base = constructor.construir()
    penalizacion = parametro_repository.obtener_valor(sesion, "penalizacion_ficticia")

    validacion = constructor.crear_validador().validar(red_base)
    if not validacion.es_valida():
        raise RedNoValidaError(validacion.mensajes)

    ajustes = [Ajuste(**a) for a in escenario.ajustes]
    try:
        red_escenario = balancear(aplicar_ajustes(red_base, ajustes), penalizacion)
    except ValueError as error:
        raise EscenarioInvalidoError(str(error)) from error
    red_base_balanceada = balancear(red_base, penalizacion)
    solucion_base = resolver_lp(red_base_balanceada)
    if solucion_base is None:
        raise EscenarioInvalidoError("La red base no tiene solución factible")

    exacto = ejecucion_service.ejecutar_exacto(sesion, red_escenario, escenario.id)
    costo_exacto = float(exacto.costo_total)

    ejecucion_ag = None
    if entrada.incluir_ag:
        ejecucion_ag = ejecucion_service.ejecutar_genetico(
            sesion, entrada.parametros_ag, red_escenario, escenario.id
        )

    solucion_escenario = resolver_lp(red_escenario)
    cambios = []
    if solucion_escenario is not None:
        for i, origen in enumerate(red_escenario.codigos_empresas):
            for j, destino in enumerate(red_escenario.codigos_plantas):
                antes = 0.0
                if destino in red_base_balanceada.codigos_plantas:
                    antes = float(
                        solucion_base.flujos[i, red_base_balanceada.codigos_plantas.index(destino)]
                    )
                despues = float(solucion_escenario.flujos[i, j])
                if abs(antes - despues) > 1e-6:
                    cambios.append(
                        CambioFlujo(
                            origen=origen,
                            destino=destino,
                            toneladas_base=round(antes, 4),
                            toneladas_escenario=round(despues, 4),
                        )
                    )

    toneladas_ficticia = 0.0
    if red_escenario.tiene_planta_ficticia() and solucion_escenario is not None:
        columna = red_escenario.codigos_plantas.index(CODIGO_PLANTA_FICTICIA)
        toneladas_ficticia = float(solucion_escenario.flujos[:, columna].sum())

    costo_ag = None if ejecucion_ag is None else float(ejecucion_ag.costo_total)
    gap = None
    if costo_ag is not None and costo_exacto > 0:
        gap = (costo_ag - costo_exacto) / costo_exacto * 100
    return ResultadoEscenario(
        escenario_id=escenario.id,
        nombre=escenario.nombre,
        costo_base=solucion_base.costo,
        costo_exacto=costo_exacto,
        variacion_porcentual=(costo_exacto - solucion_base.costo) / solucion_base.costo * 100,
        ejecucion_exacto_id=exacto.id,
        ejecucion_ag_id=None if ejecucion_ag is None else ejecucion_ag.id,
        costo_ag=costo_ag,
        gap_ag=gap,
        tiempo_exacto_ms=float(exacto.tiempo_ms),
        tiempo_ag_ms=None if ejecucion_ag is None else float(ejecucion_ag.tiempo_ms),
        usa_planta_ficticia=red_escenario.tiene_planta_ficticia(),
        toneladas_ficticia=toneladas_ficticia,
        cambios_flujo=cambios,
    )


# ---------- Rangos de estabilidad (HU-12) ----------


def _redondear(valor: float | None) -> float | None:
    return None if valor is None else round(valor, 2)


def calcular_rangos_de_ejecucion(sesion: Session, ejecucion_id: uuid.UUID) -> RangosSalida:
    ejecucion = sesion.get(Ejecucion, ejecucion_id)
    if ejecucion is None:
        raise EscenarioNoEncontradoError(f"No existe la ejecución {ejecucion_id}")
    if ejecucion.metodo != Metodo.EXACTO:
        raise EscenarioInvalidoError("Los rangos se calculan sobre una ejecución del exacto")

    red = ejecucion_service.red_desde_snapshot(ejecucion.snapshot_red)
    rangos = calcular_rangos(red)
    ids_nodos = ejecucion_repository.mapa_ids_nodos(sesion)
    ids_rutas = ejecucion_repository.mapa_ids_rutas(sesion)

    valores = {}
    for registro in sesion.execute(
        select(SensibilidadResultado).where(SensibilidadResultado.ejecucion_id == ejecucion_id)
    ).scalars():
        clave = (registro.tipo, registro.nodo_id or registro.ruta_id)
        valores[clave] = float(registro.valor)

    def guardar(tipo: str, nodo_id=None, ruta_id=None, inferior=None, superior=None) -> None:
        condicion = [
            SensibilidadResultado.ejecucion_id == ejecucion_id,
            SensibilidadResultado.tipo == tipo,
        ]
        if nodo_id is not None:
            condicion.append(SensibilidadResultado.nodo_id == nodo_id)
        else:
            condicion.append(SensibilidadResultado.ruta_id == ruta_id)
        sesion.execute(
            update(SensibilidadResultado)
            .where(*condicion)
            .values(rango_inf=_redondear(inferior), rango_sup=_redondear(superior))
        )

    salida: list[RangoSalida] = []
    for (i, j), rango in rangos.costos.items():
        origen, destino = red.codigos_empresas[i], red.codigos_plantas[j]
        if destino == CODIGO_PLANTA_FICTICIA:
            continue
        ruta_id = ids_rutas.get((origen, destino))
        salida.append(
            RangoSalida(
                tipo="COSTO_RUTA",
                elemento=f"{origen}->{destino}",
                valor=round(rango.valor, 2),
                inferior=_redondear(rango.inferior),
                superior=_redondear(rango.superior),
                dual_o_costo_reducido=valores.get((COSTO_REDUCIDO, ruta_id)),
            )
        )
        if ruta_id is not None:
            guardar(
                COSTO_REDUCIDO, ruta_id=ruta_id, inferior=rango.inferior, superior=rango.superior
            )
    for j, rango in rangos.capacidades.items():
        codigo = red.codigos_plantas[j]
        if codigo == CODIGO_PLANTA_FICTICIA:
            continue
        nodo_id = ids_nodos.get(codigo)
        salida.append(
            RangoSalida(
                tipo="CAPACIDAD",
                elemento=codigo,
                valor=round(rango.valor, 2),
                inferior=_redondear(rango.inferior),
                superior=_redondear(rango.superior),
                dual_o_costo_reducido=valores.get((DUAL_CAPACIDAD, nodo_id)),
            )
        )
        guardar(DUAL_CAPACIDAD, nodo_id=nodo_id, inferior=rango.inferior, superior=rango.superior)
    for i, rango in rangos.ofertas.items():
        codigo = red.codigos_empresas[i]
        nodo_id = ids_nodos.get(codigo)
        salida.append(
            RangoSalida(
                tipo="OFERTA",
                elemento=codigo,
                valor=round(rango.valor, 2),
                inferior=_redondear(rango.inferior),
                superior=_redondear(rango.superior),
                dual_o_costo_reducido=valores.get((DUAL_OFERTA, nodo_id)),
            )
        )
        guardar(DUAL_OFERTA, nodo_id=nodo_id, inferior=rango.inferior, superior=rango.superior)
    sesion.commit()
    return RangosSalida(ejecucion_id=ejecucion_id, rangos=salida, omitido=rangos.omitido)


def calcular_tornado(sesion: Session, porcentaje: float) -> TornadoSalida:
    red = RedBuilder(sesion).construir()
    penalizacion = parametro_repository.obtener_valor(sesion, "penalizacion_ficticia")
    base = resolver_lp(balancear(red, penalizacion))
    if base is None:
        raise EscenarioInvalidoError("La red base no tiene solución factible")
    impactos = [
        ImpactoSalida(parametro=i.parametro, costo_menos=i.costo_menos, costo_mas=i.costo_mas)
        for i in tornado(red, porcentaje, penalizacion)
    ]
    impactos.sort(
        key=lambda i: (
            -max(
                abs((i.costo_menos or base.costo) - base.costo),
                abs((i.costo_mas or base.costo) - base.costo),
            )
        )
    )
    return TornadoSalida(porcentaje=porcentaje, costo_base=base.costo, impactos=impactos)
