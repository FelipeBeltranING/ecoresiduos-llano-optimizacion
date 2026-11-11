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
    detalles: list[str] = field(default_factory=list)

    @property
    def total(self) -> float:
        return (
            self.violacion_oferta
            + self.violacion_capacidad
            + self.flujos_negativos
            + self.flujo_en_rutas_cerradas
        )

    def es_factible(self) -> bool:
        return self.total <= TOLERANCIA * 10


# Verificación de oferta (=), capacidad (<=), no negatividad y rutas habilitadas (RF-09)
def verificar_solucion(red: RedLogistica, flujos: np.ndarray) -> ReporteVerificacion:
    enviado = flujos.sum(axis=1)
    recibido = flujos.sum(axis=0)

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
    if reporte.flujo_en_rutas_cerradas > TOLERANCIA:
        reporte.detalles.append("Hay flujo en rutas deshabilitadas.")
    return reporte
