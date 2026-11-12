import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.db.models import (
    ConvergenciaAG,
    Ejecucion,
    FlujoResultado,
    Metodo,
    Nodo,
    Ruta,
    SensibilidadResultado,
)
from app.optimizacion.red import CODIGO_PLANTA_FICTICIA


# Mapas de código a id para nodos y rutas
def mapa_ids_nodos(sesion: Session) -> dict[str, uuid.UUID]:
    ids = {}
    for codigo, nodo_id in sesion.execute(select(Nodo.codigo, Nodo.id)):
        ids[codigo] = nodo_id
    return ids


def mapa_ids_rutas(sesion: Session) -> dict[tuple[str, str], uuid.UUID]:
    origen = aliased(Nodo)
    destino = aliased(Nodo)
    consulta = (
        select(origen.codigo, destino.codigo, Ruta.id)
        .join(origen, Ruta.origen_id == origen.id)
        .join(destino, Ruta.destino_id == destino.id)
    )
    ids = {}
    for codigo_origen, codigo_destino, ruta_id in sesion.execute(consulta):
        ids[(codigo_origen, codigo_destino)] = ruta_id
    return ids


# Registro de la ejecución
def crear_ejecucion(
    sesion: Session,
    metodo: Metodo,
    estado: str,
    costo_total: float,
    tiempo_ms: float,
    parametros: dict | None,
    snapshot_red: dict,
    escenario_id: uuid.UUID | None = None,
    violaciones: float | None = None,
) -> Ejecucion:
    ejecucion = Ejecucion(
        metodo=metodo,
        estado=estado,
        costo_total=costo_total,
        tiempo_ms=tiempo_ms,
        parametros=parametros,
        snapshot_red=snapshot_red,
        escenario_id=escenario_id,
        violaciones=violaciones,
    )
    sesion.add(ejecucion)
    sesion.flush()
    return ejecucion


# Registro de un flujo (destino nulo = planta ficticia)
def agregar_flujo(
    sesion: Session,
    ejecucion_id: uuid.UUID,
    origen_id: uuid.UUID,
    destino_id: uuid.UUID | None,
    toneladas: float,
    costo_unitario: float,
) -> None:
    flujo = FlujoResultado(
        ejecucion_id=ejecucion_id,
        origen_id=origen_id,
        destino_id=destino_id,
        toneladas=toneladas,
        costo_unitario=costo_unitario,
    )
    sesion.add(flujo)


# Registro de un dual, holgura o costo reducido
def agregar_sensibilidad(
    sesion: Session,
    ejecucion_id: uuid.UUID,
    tipo: str,
    valor: float,
    nodo_id: uuid.UUID | None = None,
    ruta_id: uuid.UUID | None = None,
) -> None:
    registro = SensibilidadResultado(
        ejecucion_id=ejecucion_id, tipo=tipo, valor=valor, nodo_id=nodo_id, ruta_id=ruta_id
    )
    sesion.add(registro)


# Registro de una generación del AG
def agregar_convergencia(
    sesion: Session,
    ejecucion_id: uuid.UUID,
    generacion: int,
    mejor_costo: float,
    costo_promedio: float,
) -> None:
    registro = ConvergenciaAG(
        ejecucion_id=ejecucion_id,
        generacion=generacion,
        mejor_costo=mejor_costo,
        costo_promedio=costo_promedio,
    )
    sesion.add(registro)


# Consultas del detalle de una ejecución
def buscar_ejecucion(sesion: Session, ejecucion_id: uuid.UUID) -> Ejecucion | None:
    return sesion.get(Ejecucion, ejecucion_id)


def listar_flujos(sesion: Session, ejecucion_id: uuid.UUID) -> list[tuple[str, str, float, float]]:
    origen = aliased(Nodo)
    destino = aliased(Nodo)
    consulta = (
        select(
            origen.codigo, destino.codigo, FlujoResultado.toneladas, FlujoResultado.costo_unitario
        )
        .join(origen, FlujoResultado.origen_id == origen.id)
        .outerjoin(destino, FlujoResultado.destino_id == destino.id)
        .where(FlujoResultado.ejecucion_id == ejecucion_id)
        .order_by(origen.codigo, destino.codigo)
    )
    flujos = []
    for codigo_origen, codigo_destino, toneladas, costo_unitario in sesion.execute(consulta):
        if codigo_destino is None:
            codigo_destino = CODIGO_PLANTA_FICTICIA
        flujos.append((codigo_origen, codigo_destino, float(toneladas), float(costo_unitario)))
    return flujos


def listar_sensibilidad(sesion: Session, ejecucion_id: uuid.UUID) -> list[dict]:
    nodo = aliased(Nodo)
    origen = aliased(Nodo)
    destino = aliased(Nodo)
    consulta = (
        select(SensibilidadResultado, nodo.codigo, origen.codigo, destino.codigo)
        .outerjoin(nodo, SensibilidadResultado.nodo_id == nodo.id)
        .outerjoin(Ruta, SensibilidadResultado.ruta_id == Ruta.id)
        .outerjoin(origen, Ruta.origen_id == origen.id)
        .outerjoin(destino, Ruta.destino_id == destino.id)
        .where(SensibilidadResultado.ejecucion_id == ejecucion_id)
        .order_by(SensibilidadResultado.tipo, nodo.codigo, origen.codigo, destino.codigo)
    )
    registros = []
    for registro, codigo_nodo, codigo_origen, codigo_destino in sesion.execute(consulta):
        elemento = codigo_nodo
        if elemento is None:
            elemento = f"{codigo_origen}->{codigo_destino}"
        registros.append(
            {
                "tipo": registro.tipo,
                "elemento": elemento,
                "valor": registro.valor,
                "rango_inf": registro.rango_inf,
                "rango_sup": registro.rango_sup,
            }
        )
    return registros


def listar_convergencia(sesion: Session, ejecucion_id: uuid.UUID) -> list[ConvergenciaAG]:
    consulta = (
        select(ConvergenciaAG)
        .where(ConvergenciaAG.ejecucion_id == ejecucion_id)
        .order_by(ConvergenciaAG.generacion)
    )
    return list(sesion.execute(consulta).scalars())
