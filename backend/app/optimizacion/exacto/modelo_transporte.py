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


# Flujo de costo mínimo con PuLP + CBC (HU-07); sin acopios es el modelo de transporte
class ModeloTransporte:
    def __init__(self, red: RedLogistica) -> None:
        self.red = red
        self.problema = pulp.LpProblem("transporte_ecoresiduos", pulp.LpMinimize)
        self.variables: dict[tuple[int, int], pulp.LpVariable] = {}
        self.restricciones_oferta: list[str] = []
        self.restricciones_capacidad: list[str] = []
        # Arcos de los centros de acopio (HU-17): empresa → acopio y acopio → planta
        self.variables_a_acopio: dict[tuple[int, int], pulp.LpVariable] = {}
        self.variables_desde_acopio: dict[tuple[int, int], pulp.LpVariable] = {}
        self.restricciones_acopio: list[str] = []
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

        self._crear_variables_de_acopios()

        # Función objetivo: costo de todos los arcos (transporte + manejo + operación)
        terminos = [red.costos[i, j] * v for (i, j), v in self.variables.items()]
        terminos += [red.costos_a_acopio[i, t] * v for (i, t), v in self.variables_a_acopio.items()]
        terminos += [
            red.costos_desde_acopio[t, j] * v for (t, j), v in self.variables_desde_acopio.items()
        ]
        self.problema += pulp.lpSum(terminos)

        # Cada empresa envía toda su oferta (a plantas o a acopios)
        for i, codigo_empresa in enumerate(red.codigos_empresas):
            nombre = f"oferta_{codigo_empresa}"
            fila = [v for (fi, _), v in self.variables.items() if fi == i]
            fila += [v for (fi, _), v in self.variables_a_acopio.items() if fi == i]
            self.problema += pulp.lpSum(fila) == red.oferta[i], nombre
            self.restricciones_oferta.append(nombre)

        # Ninguna planta recibe más de su capacidad (desde empresas o desde acopios)
        for j, codigo_planta in enumerate(red.codigos_plantas):
            nombre = f"capacidad_{codigo_planta}"
            columna = [v for (_, cj), v in self.variables.items() if cj == j]
            columna += [v for (_, cj), v in self.variables_desde_acopio.items() if cj == j]
            self.problema += pulp.lpSum(columna) <= red.capacidad[j], nombre
            self.restricciones_capacidad.append(nombre)

        # Lo que entra a un acopio sale de él, y cabe en el acopio
        for t, codigo_acopio in enumerate(red.codigos_acopios):
            entra = [v for (_, ct), v in self.variables_a_acopio.items() if ct == t]
            sale = [v for (ft, _), v in self.variables_desde_acopio.items() if ft == t]
            self.problema += pulp.lpSum(entra) == pulp.lpSum(sale), f"conservacion_{codigo_acopio}"
            nombre = f"capacidad_{codigo_acopio}"
            self.problema += pulp.lpSum(entra) <= red.capacidad_acopios[t], nombre
            self.restricciones_acopio.append(nombre)

    def _crear_variables_de_acopios(self) -> None:
        red = self.red
        for t, codigo_acopio in enumerate(red.codigos_acopios):
            for i, codigo_empresa in enumerate(red.codigos_empresas):
                if red.rutas_a_acopio[i, t]:
                    nombre = f"x_{codigo_empresa}_{codigo_acopio}"
                    self.variables_a_acopio[(i, t)] = pulp.LpVariable(nombre, lowBound=0)
            for j, codigo_planta in enumerate(red.codigos_plantas):
                if red.rutas_desde_acopio[t, j]:
                    nombre = f"x_{codigo_acopio}_{codigo_planta}"
                    self.variables_desde_acopio[(t, j)] = pulp.LpVariable(nombre, lowBound=0)

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
        recibido = flujos.sum(axis=0)
        acopios = self._resultado_de_acopios()
        if acopios:
            recibido = recibido + acopios["flujos_desde_acopio"].sum(axis=0)
        holguras = self.red.capacidad - recibido
        holguras[np.abs(holguras) < 1e-9] = 0.0

        costo_total = pulp.value(self.problema.objective)
        return {
            **acopios,
            "estado": estado,
            "costo_total": float(costo_total) if costo_total is not None else 0.0,
            "flujos": flujos,
            "duales_oferta": duales_oferta + 0.0,
            "duales_capacidad": duales_capacidad + 0.0,
            "costos_reducidos": costos_reducidos + 0.0,
            "holguras": holguras,
            "tiempo_ms": tiempo_ms,
        }

    # Flujos por arco, duales y holguras de los acopios (vacío si la red no tiene acopios)
    def _resultado_de_acopios(self) -> dict:
        red = self.red
        if not red.tiene_acopios():
            return {}
        a_acopio = np.zeros((red.numero_empresas(), red.numero_acopios()))
        desde_acopio = np.zeros((red.numero_acopios(), red.numero_plantas()))
        for (i, t), variable in self.variables_a_acopio.items():
            a_acopio[i, t] = variable.varValue or 0.0
        for (t, j), variable in self.variables_desde_acopio.items():
            desde_acopio[t, j] = variable.varValue or 0.0
        holguras = red.capacidad_acopios - a_acopio.sum(axis=0)
        holguras[np.abs(holguras) < 1e-9] = 0.0
        duales = np.array([self._dual(nombre) for nombre in self.restricciones_acopio])
        return {
            "flujos_a_acopio": a_acopio,
            "flujos_desde_acopio": desde_acopio,
            "duales_acopio": duales + 0.0,
            "holguras_acopio": holguras,
        }
