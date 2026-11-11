from app.optimizacion.red import DatosEmpresa, DatosPlanta, DatosRuta, RedLogistica, construir_red
from app.services.caso_base_datos import DISTANCIAS_KM, EMPRESAS, ORDEN_PLANTAS, PLANTAS

COSTO_KM_CASO_BASE = 350
PENALIZACION_FICTICIA = 1_000_000
Z_OPTIMO_CASO_BASE = 64_691_000


# Red del caso base armada sin base de datos
def construir_red_caso_base(factor_oferta: float = 1.0) -> RedLogistica:
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

    return construir_red(empresas, plantas, rutas, COSTO_KM_CASO_BASE)
