from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.db.models import Nodo, ParametroGlobal, Ruta, TipoNodo
from app.optimizacion.red import calcular_costo_unitario
from app.repositories import parametro_repository
from app.schemas.gestion import (
    MatrizRutas,
    NodoActualizacion,
    NodoEntrada,
    NodoSalida,
    ParametroSalida,
    ResumenLote,
    RutaCambio,
    RutaSalida,
)
from app.services.distancias import FUENTE_MANUAL, medir_ruta


class NoEncontradoError(Exception):
    pass


class ConflictoError(Exception):
    pass




def a_salida(nodo: Nodo) -> NodoSalida:
    return NodoSalida(
        id=nodo.id,
        codigo=nodo.codigo,
        tipo=nodo.tipo,
        nombre=nodo.nombre,
        municipio=nodo.municipio,
        tipo_residuo=nodo.tipo_residuo,
        oferta_t=None if nodo.oferta_t is None else float(nodo.oferta_t),
        capacidad_t=None if nodo.capacidad_t is None else float(nodo.capacidad_t),
        costo_operacion_t=float(nodo.costo_operacion_t),
        latitud=float(nodo.latitud),
        longitud=float(nodo.longitud),
        activo=nodo.activo,
    )


def listar_nodos(
    sesion: Session, tipo: TipoNodo | None = None, incluir_inactivos: bool = True
) -> list[NodoSalida]:
    consulta = select(Nodo).order_by(Nodo.tipo, Nodo.codigo)
    if tipo is not None:
        consulta = consulta.where(Nodo.tipo == tipo)
    if not incluir_inactivos:
        consulta = consulta.where(Nodo.activo.is_(True))
    return [a_salida(nodo) for nodo in sesion.execute(consulta).scalars()]


def buscar_nodo(sesion: Session, codigo: str) -> Nodo:
    nodo = sesion.execute(select(Nodo).where(Nodo.codigo == codigo)).scalar_one_or_none()
    if nodo is None:
        raise NoEncontradoError(f"No existe el nodo {codigo}")
    return nodo


def tipos_destino(tipo: TipoNodo) -> list[TipoNodo]:
    if tipo == TipoNodo.FUENTE:
        return [TipoNodo.PLANTA, TipoNodo.ACOPIO]
    if tipo == TipoNodo.ACOPIO:
        return [TipoNodo.PLANTA]
    return []


def tipos_origen(tipo: TipoNodo) -> list[TipoNodo]:
    if tipo == TipoNodo.PLANTA:
        return [TipoNodo.FUENTE, TipoNodo.ACOPIO]
    if tipo == TipoNodo.ACOPIO:
        return [TipoNodo.FUENTE]
    return []


def crear_ruta_estimada(sesion: Session, origen: Nodo, destino: Nodo) -> None:
    medida = medir_ruta(
        float(origen.latitud),
        float(origen.longitud),
        float(destino.latitud),
        float(destino.longitud),
    )
    sesion.add(Ruta(origen_id=origen.id, destino_id=destino.id, **medida))


def generar_rutas_de_nodo(sesion: Session, nodo: Nodo) -> int:
    existentes = {(o, d) for o, d in sesion.execute(select(Ruta.origen_id, Ruta.destino_id)).all()}
    creadas = 0
    destinos = tipos_destino(nodo.tipo)
    if destinos:
        for destino in sesion.execute(select(Nodo).where(Nodo.tipo.in_(destinos))).scalars():
            if (nodo.id, destino.id) not in existentes:
                crear_ruta_estimada(sesion, nodo, destino)
                creadas += 1
    origenes = tipos_origen(nodo.tipo)
    if origenes:
        for origen in sesion.execute(select(Nodo).where(Nodo.tipo.in_(origenes))).scalars():
            if (origen.id, nodo.id) not in existentes:
                crear_ruta_estimada(sesion, origen, nodo)
                creadas += 1
    return creadas


def crear_nodo(sesion: Session, entrada: NodoEntrada) -> NodoSalida:
    existe = sesion.execute(select(Nodo.id).where(Nodo.codigo == entrada.codigo)).first()
    if existe:
        raise ConflictoError(f"Ya existe un nodo con el código {entrada.codigo}")
    datos = entrada.model_dump()
    if entrada.tipo == TipoNodo.FUENTE:
        datos["capacidad_t"] = None
    else:
        datos["oferta_t"] = None
    nodo = Nodo(**datos, activo=True)
    try:
        sesion.add(nodo)
        sesion.flush()
        generar_rutas_de_nodo(sesion, nodo)
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    sesion.refresh(nodo)
    return a_salida(nodo)


def actualizar_nodo(sesion: Session, codigo: str, cambios: NodoActualizacion) -> NodoSalida:
    nodo = buscar_nodo(sesion, codigo)
    datos = cambios.model_dump(exclude_unset=True)
    if nodo.tipo == TipoNodo.FUENTE and datos.get("capacidad_t") is not None:
        raise ConflictoError("Una empresa no tiene capacidad, solo oferta")
    if nodo.tipo != TipoNodo.FUENTE and datos.get("oferta_t") is not None:
        raise ConflictoError("Una planta o acopio no tiene oferta, solo capacidad")
    for campo, valor in datos.items():
        setattr(nodo, campo, valor)
    sesion.commit()
    sesion.refresh(nodo)
    return a_salida(nodo)


def desactivar_nodo(sesion: Session, codigo: str) -> NodoSalida:
    return actualizar_nodo(sesion, codigo, NodoActualizacion(activo=False))




def obtener_matriz(sesion: Session) -> MatrizRutas:
    costo_km_global = parametro_repository.obtener_valor(sesion, "costo_km_t")
    origen = aliased(Nodo)
    destino = aliased(Nodo)
    consulta = (
        select(Ruta, origen, destino)
        .join(origen, Ruta.origen_id == origen.id)
        .join(destino, Ruta.destino_id == destino.id)
        .where(origen.activo.is_(True), destino.activo.is_(True))
        .order_by(origen.codigo, destino.codigo)
    )
    rutas = []
    origenes: list[str] = []
    destinos: list[str] = []
    for ruta, nodo_origen, nodo_destino in sesion.execute(consulta):
        distancia = None if ruta.distancia_km is None else float(ruta.distancia_km)
        costo_km = None if ruta.costo_km_t is None else float(ruta.costo_km_t)
        costo_unitario = None
        if distancia is not None:
            costo_unitario = calcular_costo_unitario(
                distancia, costo_km, costo_km_global, float(nodo_destino.costo_operacion_t)
            )
        rutas.append(
            RutaSalida(
                origen=nodo_origen.codigo,
                destino=nodo_destino.codigo,
                distancia_km=distancia,
                costo_km_t=costo_km,
                habilitada=ruta.habilitada,
                costo_unitario=costo_unitario,
                duracion_min=None if ruta.duracion_min is None else float(ruta.duracion_min),
                fuente_distancia=ruta.fuente_distancia,
                geometria=ruta.geometria,
            )
        )
        if nodo_origen.codigo not in origenes:
            origenes.append(nodo_origen.codigo)
        if nodo_destino.codigo not in destinos:
            destinos.append(nodo_destino.codigo)
    return MatrizRutas(origenes=origenes, destinos=sorted(destinos), rutas=rutas)


def actualizar_rutas(sesion: Session, cambios: list[RutaCambio]) -> ResumenLote:
    ids = {codigo: nodo_id for codigo, nodo_id in sesion.execute(select(Nodo.codigo, Nodo.id))}
    actualizadas = 0
    creadas = 0
    try:
        for cambio in cambios:
            if cambio.origen not in ids or cambio.destino not in ids:
                raise NoEncontradoError(f"Ruta {cambio.origen}->{cambio.destino}: nodo inexistente")
            if cambio.origen == cambio.destino:
                raise ConflictoError("El origen y el destino de una ruta deben ser distintos")
            ruta = sesion.execute(
                select(Ruta).where(
                    Ruta.origen_id == ids[cambio.origen], Ruta.destino_id == ids[cambio.destino]
                )
            ).scalar_one_or_none()
            if ruta is None:
                ruta = Ruta(origen_id=ids[cambio.origen], destino_id=ids[cambio.destino])
                sesion.add(ruta)
                creadas += 1
            else:
                actualizadas += 1
            if cambio.distancia_km is not None:
                ruta.distancia_km = cambio.distancia_km
                ruta.fuente_distancia = FUENTE_MANUAL
            if cambio.costo_km_t is not None:
                ruta.costo_km_t = cambio.costo_km_t
            if cambio.quitar_costo_km_t:
                ruta.costo_km_t = None
            if cambio.habilitada is not None:
                ruta.habilitada = cambio.habilitada
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    return ResumenLote(actualizadas=actualizadas, creadas=creadas)


def generar_rutas_faltantes(sesion: Session) -> ResumenLote:
    creadas = 0
    try:
        for nodo in sesion.execute(select(Nodo)).scalars():
            creadas += generar_rutas_de_nodo(sesion, nodo)
            sesion.flush()
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise
    return ResumenLote(actualizadas=0, creadas=creadas)




def listar_parametros(sesion: Session) -> list[ParametroSalida]:
    consulta = select(ParametroGlobal).order_by(ParametroGlobal.clave)
    return [
        ParametroSalida(
            clave=p.clave, valor=float(p.valor), unidad=p.unidad, descripcion=p.descripcion
        )
        for p in sesion.execute(consulta).scalars()
    ]


def actualizar_parametro(sesion: Session, clave: str, valor: float) -> ParametroSalida:
    parametro = sesion.get(ParametroGlobal, clave)
    if parametro is None:
        raise NoEncontradoError(f"No existe el parámetro {clave}")
    if clave in ("penalizacion_ficticia", "lambda_ag") and valor <= 0:
        raise ConflictoError(f"El parámetro {clave} debe ser mayor que cero")
    parametro.valor = valor
    sesion.commit()
    return ParametroSalida(
        clave=parametro.clave,
        valor=float(parametro.valor),
        unidad=parametro.unidad,
        descripcion=parametro.descripcion,
    )
