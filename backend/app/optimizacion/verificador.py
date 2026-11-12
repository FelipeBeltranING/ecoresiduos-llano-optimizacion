from dataclasses import dataclass, field

import numpy as np

from app.optimizacion.red import RedLogistica

TOLERANCIA = 1e-6


# Resultado de revisar una solución contra las restricciones del modelo
@dataclass
class ReporteVerificacion:
    violacion_oferta: float
    violacion_capacidad: float
    flujos_negativos: float
    flujo_en_rutas_cerradas: float
    violacion_conservacion: float = 0.0
    violacion_acopio: float = 0.0
    detalles: list[str] = field(default_factory=list)

    @property
    def total(self) -> float:
        return (
            self.violacion_oferta
            + self.violacion_capacidad
            + self.flujos_negativos
            + self.flujo_en_rutas_cerradas
            + self.violacion_conservacion
            + self.violacion_acopio
        )

    def es_factible(self) -> bool:
        return self.total <= TOLERANCIA * 10


# Verificación de oferta (=), capacidad (<=), no negatividad y rutas habilitadas (RF-09)
# Con acopios revisa además la conservación de flujo y la capacidad de cada acopio (HU-17)
def verificar_solucion(
    red: RedLogistica,
    flujos: np.ndarray,
    flujos_a_acopio: np.ndarray | None = None,
    flujos_desde_acopio: np.ndarray | None = None,
) -> ReporteVerificacion:
    enviado = flujos.sum(axis=1)
    recibido = flujos.sum(axis=0)
    con_acopios = red.tiene_acopios() and flujos_a_acopio is not None
    if con_acopios:
        enviado = enviado + flujos_a_acopio.sum(axis=1)
        recibido = recibido + flujos_desde_acopio.sum(axis=0)

    exceso_oferta = np.abs(enviado - red.oferta)
    exceso_capacidad = np.maximum(0.0, recibido - red.capacidad)
    negativos = np.maximum(0.0, -flujos)
    cerradas = np.where(red.rutas_habilitadas, 0.0, np.abs(flujos))

    reporte = ReporteVerificacion(
        violacion_oferta=float(np.where(exceso_oferta > TOLERANCIA, exceso_oferta, 0).sum()),
        violacion_capacidad=float(
            np.where(exceso_capacidad > TOLERANCIA, exceso_capacidad, 0).sum()
        ),
        flujos_negativos=float(np.where(negativos > TOLERANCIA, negativos, 0).sum()),
        flujo_en_rutas_cerradas=float(np.where(cerradas > TOLERANCIA, cerradas, 0).sum()),
    )

    for i, codigo in enumerate(red.codigos_empresas):
        if exceso_oferta[i] > TOLERANCIA:
            reporte.detalles.append(
                f"Oferta de {codigo}: se enviaron {enviado[i]:.2f} t de {red.oferta[i]:.2f} t."
            )
    for j, codigo in enumerate(red.codigos_plantas):
        if exceso_capacidad[j] > TOLERANCIA:
            reporte.detalles.append(
                f"Capacidad de {codigo}: recibe {recibido[j]:.2f} t y admite "
                f"{red.capacidad[j]:.2f} t."
            )
    if con_acopios:
        verificar_acopios(red, flujos_a_acopio, flujos_desde_acopio, reporte)
    if reporte.flujo_en_rutas_cerradas > TOLERANCIA:
        reporte.detalles.append("Hay flujo en rutas deshabilitadas.")
    return reporte


# Acopios: lo que entra es igual a lo que sale, cabe en el acopio y usa arcos abiertos
def verificar_acopios(
    red: RedLogistica, a_acopio: np.ndarray, desde_acopio: np.ndarray, reporte: ReporteVerificacion
) -> None:
    entra = a_acopio.sum(axis=0)
    sale = desde_acopio.sum(axis=1)
    desbalance = np.abs(entra - sale)
    exceso = np.maximum(0.0, entra - red.capacidad_acopios)

    reporte.violacion_conservacion = float(np.where(desbalance > TOLERANCIA, desbalance, 0).sum())
    reporte.violacion_acopio = float(np.where(exceso > TOLERANCIA, exceso, 0).sum())
    for arcos, abiertos in ((a_acopio, red.rutas_a_acopio), (desde_acopio, red.rutas_desde_acopio)):
        negativos = np.maximum(0.0, -arcos)
        cerrados = np.where(abiertos, 0.0, np.abs(arcos))
        reporte.flujos_negativos += float(np.where(negativos > TOLERANCIA, negativos, 0).sum())
        reporte.flujo_en_rutas_cerradas += float(np.where(cerrados > TOLERANCIA, cerrados, 0).sum())

    for t, codigo in enumerate(red.codigos_acopios):
        if desbalance[t] > TOLERANCIA:
            reporte.detalles.append(
                f"Acopio {codigo}: entran {entra[t]:.2f} t y salen {sale[t]:.2f} t."
            )
        if exceso[t] > TOLERANCIA:
            reporte.detalles.append(
                f"Capacidad del acopio {codigo}: recibe {entra[t]:.2f} t y admite "
                f"{red.capacidad_acopios[t]:.2f} t."
            )
