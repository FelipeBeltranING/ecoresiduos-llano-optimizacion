import time

import numpy as np
import pulp

from app.optimizacion.red import RedLogistica

ESTADOS_PULP = {
    "Optimal": "Óptimo",
    "Infeasible": "Infactible",
    "Unbounded": "No acotado",
    "Not Solved": "No resuelto",
    "Undefined": "Indefinido",
}


# Modelo de transporte con PuLP + CBC (HU-07)
class ModeloTransporte:
    def __init__(self, red: RedLogistica) -> None:
        self.red = red
        self.problema = pulp.LpProblem("transporte_ecoresiduos", pulp.LpMinimize)
        self.variables: dict[tuple[int, int], pulp.LpVariable] = {}
        self.restricciones_oferta: list[str] = []
        self.restricciones_capacidad: list[str] = []
        self._construir()

    # Variables solo en las rutas habilitadas; las demás valen cero
    def _construir(self) -> None:
        red = self.red
        for i, codigo_empresa in enumerate(red.codigos_empresas):
            for j, codigo_planta in enumerate(red.codigos_plantas):
                if not red.rutas_habilitadas[i, j]:
                    continue
                nombre = f"x_{codigo_empresa}_{codigo_planta}"
                self.variables[(i, j)] = pulp.LpVariable(nombre, lowBound=0)

        self.problema += pulp.lpSum(
            red.costos[i, j] * variable for (i, j), variable in self.variables.items()
        )

        for i, codigo_empresa in enumerate(red.codigos_empresas):
            nombre = f"oferta_{codigo_empresa}"
            fila = [v for (fi, _), v in self.variables.items() if fi == i]
            self.problema += pulp.lpSum(fila) == red.oferta[i], nombre
            self.restricciones_oferta.append(nombre)

        for j, codigo_planta in enumerate(red.codigos_plantas):
            nombre = f"capacidad_{codigo_planta}"
            columna = [v for (_, cj), v in self.variables.items() if cj == j]
            self.problema += pulp.lpSum(columna) <= red.capacidad[j], nombre
            self.restricciones_capacidad.append(nombre)

    def _dual(self, nombre: str) -> float:
        restriccion = self.problema.get_constraint_by_name(nombre)
        return float(restriccion.pi or 0.0)

    def resolver(self) -> dict:
        inicio = time.perf_counter()
        self.problema.solve(pulp.PULP_CBC_CMD(msg=0))
        tiempo_ms = (time.perf_counter() - inicio) * 1000

        m = self.red.numero_empresas()
        n = self.red.numero_plantas()
        estado = ESTADOS_PULP.get(pulp.LpStatus[self.problema.status], "Indefinido")

        flujos = np.zeros((m, n))
        costos_reducidos = np.zeros((m, n))
        for (i, j), variable in self.variables.items():
            flujos[i, j] = variable.varValue or 0.0
            costos_reducidos[i, j] = variable.dj or 0.0

        duales_oferta = np.array([self._dual(nombre) for nombre in self.restricciones_oferta])
        duales_capacidad = np.array(
            [self._dual(nombre) for nombre in self.restricciones_capacidad]
        )
        holguras = np.array([self.red.capacidad[j] - flujos[:, j].sum() for j in range(n)])
        holguras[np.abs(holguras) < 1e-9] = 0.0

        costo_total = pulp.value(self.problema.objective)
        return {
            "estado": estado,
            "costo_total": float(costo_total) if costo_total is not None else 0.0,
            "flujos": flujos,
            "duales_oferta": duales_oferta + 0.0,
            "duales_capacidad": duales_capacidad + 0.0,
            "costos_reducidos": costos_reducidos + 0.0,
            "holguras": holguras,
            "tiempo_ms": tiempo_ms,
        }
