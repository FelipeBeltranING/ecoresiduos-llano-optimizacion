from app.optimizacion.red import (
    DatosAcopio,
    DatosEmpresa,
    DatosPlanta,
    DatosRuta,
    RedLogistica,
    construir_red,
)
from app.services.caso_base_datos import (
    ACOPIOS,
    COSTO_KM_CONSOLIDADO,
    DISTANCIAS_KM,
    EMPRESAS,
    ORDEN_PLANTAS,
    PLANTAS,
)
from app.services.distancias import distancia_vial_estimada

COSTO_KM_CASO_BASE = 350
PENALIZACION_FICTICIA = 1_000_000
Z_OPTIMO_CASO_BASE = 64_691_000
# Caso base + acopios de Puerto López y San Martín (HU-17)
Z_OPTIMO_CON_ACOPIOS = 61_761_025
TONELADAS_POR_ACOPIO = [160, 85]


# Red del caso base armada sin base de datos
def construir_red_caso_base(
    factor_oferta: float = 1.0, con_acopios: bool = False, capacidad_acopio: float | None = None
) -> RedLogistica:
    empresas = []
    for empresa in EMPRESAS:
        oferta = empresa["oferta_t"] * factor_oferta
        empresas.append(DatosEmpresa(codigo=empresa["codigo"], oferta=oferta))

    plantas = []
    for planta in PLANTAS:
        plantas.append(
            DatosPlanta(
                codigo=planta["codigo"],
                capacidad=planta["capacidad_t"],
                costo_operacion=planta["costo_operacion_t"],
            )
        )

    rutas = []
    for codigo_empresa, distancias in DISTANCIAS_KM.items():
        for posicion, codigo_planta in enumerate(ORDEN_PLANTAS):
            rutas.append(
                DatosRuta(
                    origen=codigo_empresa,
                    destino=codigo_planta,
                    distancia_km=distancias[posicion],
                    costo_km_t=None,
                    habilitada=True,
                )
            )

    acopios = None
    if con_acopios:
        acopios = []
        for acopio in ACOPIOS:
            capacidad = acopio["capacidad_t"] if capacidad_acopio is None else capacidad_acopio
            acopios.append(DatosAcopio(acopio["codigo"], capacidad, acopio["costo_operacion_t"]))
            rutas += rutas_del_acopio(acopio)

    return construir_red(empresas, plantas, rutas, COSTO_KM_CASO_BASE, acopios)


# Rutas empresa → acopio (flete directo) y acopio → planta (flete consolidado)
def rutas_del_acopio(acopio: dict) -> list[DatosRuta]:
    rutas = []
    for empresa in EMPRESAS:
        distancia = distancia_vial_estimada(
            empresa["latitud"], empresa["longitud"], acopio["latitud"], acopio["longitud"]
        )
        rutas.append(DatosRuta(empresa["codigo"], acopio["codigo"], distancia, None, True))
    for planta in PLANTAS:
        distancia = distancia_vial_estimada(
            acopio["latitud"], acopio["longitud"], planta["latitud"], planta["longitud"]
        )
        rutas.append(
            DatosRuta(acopio["codigo"], planta["codigo"], distancia, COSTO_KM_CONSOLIDADO, True)
        )
    return rutas
