from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.db.models import Nodo, Ruta, TipoNodo
from app.optimizacion.red import (
    DatosEmpresa,
    DatosPlanta,
    DatosRuta,
    RedLogistica,
    ValidadorRed,
    construir_red,
)
from app.repositories import parametro_repository


# Armado de la RedLogistica a partir de la base de datos
class RedBuilder:
    def __init__(self, sesion: Session) -> None:
        self.sesion = sesion

    def leer_empresas(self) -> list[DatosEmpresa]:
        consulta = (
            select(Nodo)
            .where(Nodo.tipo == TipoNodo.FUENTE, Nodo.activo.is_(True))
            .order_by(Nodo.codigo)
        )
        empresas = []
        for nodo in self.sesion.execute(consulta).scalars():
            oferta = 0.0
            if nodo.oferta_t is not None:
                oferta = float(nodo.oferta_t)
            empresas.append(DatosEmpresa(codigo=nodo.codigo, oferta=oferta))
        return empresas

    def leer_plantas(self) -> list[DatosPlanta]:
        consulta = (
            select(Nodo)
            .where(Nodo.tipo == TipoNodo.PLANTA, Nodo.activo.is_(True))
            .order_by(Nodo.codigo)
        )
        plantas = []
        for nodo in self.sesion.execute(consulta).scalars():
            capacidad = 0.0
            if nodo.capacidad_t is not None:
                capacidad = float(nodo.capacidad_t)
            plantas.append(
                DatosPlanta(
                    codigo=nodo.codigo,
                    capacidad=capacidad,
                    costo_operacion=float(nodo.costo_operacion_t),
                )
            )
        return plantas

    def leer_rutas(self) -> list[DatosRuta]:
        origen = aliased(Nodo)
        destino = aliased(Nodo)
        consulta = (
            select(Ruta, origen.codigo, destino.codigo)
            .join(origen, Ruta.origen_id == origen.id)
            .join(destino, Ruta.destino_id == destino.id)
        )
        rutas = []
        for ruta, codigo_origen, codigo_destino in self.sesion.execute(consulta):
            distancia = None
            if ruta.distancia_km is not None:
                distancia = float(ruta.distancia_km)
            costo_km = None
            if ruta.costo_km_t is not None:
                costo_km = float(ruta.costo_km_t)
            rutas.append(
                DatosRuta(
                    origen=codigo_origen,
                    destino=codigo_destino,
                    distancia_km=distancia,
                    costo_km_t=costo_km,
                    habilitada=ruta.habilitada,
                )
            )
        return rutas

    def construir(self) -> RedLogistica:
        costo_km_global = parametro_repository.obtener_valor(self.sesion, "costo_km_t")
        return construir_red(
            self.leer_empresas(), self.leer_plantas(), self.leer_rutas(), costo_km_global
        )

    def crear_validador(self) -> ValidadorRed:
        penalizacion = parametro_repository.obtener_valor(self.sesion, "penalizacion_ficticia")
        return ValidadorRed(penalizacion_ficticia=penalizacion)
