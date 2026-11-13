import numpy as np
import pulp
from abc import ABC, abstractmethod


class ModeloFlujoCostoMinimo(ABC):

    def __init__(self, costos, oferta, demanda):
        self.costos = np.array(costos, dtype=float)
        self.oferta = np.array(oferta, dtype=float)
        self.demanda = np.array(demanda, dtype=float)
        self.asignacion = None
        self.costo_total = None

    @abstractmethod
    def resolver(self):
        pass


class ModeloTransporte(ModeloFlujoCostoMinimo):

    def __init__(self, costos, oferta, demanda):
        super().__init__(costos, oferta, demanda)
        self.balanceado = False
        self._balancear()

    def _balancear(self):
        so, sd = self.oferta.sum(), self.demanda.sum()
        if np.isclose(so, sd):
            self.balanceado = True
            return
        if so > sd:
            dif = so - sd
            self.demanda = np.append(self.demanda, dif)
            self.costos = np.hstack([self.costos, np.zeros((self.costos.shape[0], 1))])
        else:
            dif = sd - so
            self.oferta = np.append(self.oferta, dif)
            self.costos = np.vstack([self.costos, np.zeros((1, self.costos.shape[1]))])
        self.balanceado = False

    def _vogel_inicial(self):
        m, n = self.costos.shape
        oferta = self.oferta.copy()
        demanda = self.demanda.copy()
        asignacion = np.zeros((m, n))
        filas, cols = list(range(m)), list(range(n))

        while filas and cols:
            pen_f = []
            for i in filas:
                v = sorted(self.costos[i, cols])
                pen_f.append((v[1] - v[0] if len(v) >= 2 else 0.0, i))
            pen_c = []
            for j in cols:
                v = sorted(self.costos[filas, j])
                pen_c.append((v[1] - v[0] if len(v) >= 2 else 0.0, j))

            max_f = max(pen_f, key=lambda x: x[0])
            max_c = max(pen_c, key=lambda x: x[0])

            if max_f[0] >= max_c[0]:
                i = max_f[1]
                j = min(cols, key=lambda c: self.costos[i, c])
            else:
                j = max_c[1]
                i = min(filas, key=lambda f: self.costos[f, j])

            cant = min(oferta[i], demanda[j])
            asignacion[i, j] = cant
            oferta[i] -= cant
            demanda[j] -= cant

            if np.isclose(oferta[i], 0):
                filas.remove(i)
            if np.isclose(demanda[j], 0):
                cols.remove(j)

        self.asignacion = asignacion
        return asignacion

    def _potenciales(self):
        m, n = self.costos.shape
        u = np.full(m, np.nan)
        v = np.full(n, np.nan)
        u[0] = 0.0

        basicas = [(i, j) for i in range(m) for j in range(n)
                   if not np.isclose(self.asignacion[i, j], 0)]

        cambio = True
        while cambio:
            cambio = False
            for i, j in basicas:
                if not np.isnan(u[i]) and np.isnan(v[j]):
                    v[j] = self.costos[i, j] - u[i]
                    cambio = True
                elif np.isnan(u[i]) and not np.isnan(v[j]):
                    u[i] = self.costos[i, j] - v[j]
                    cambio = True
        return u, v

    def _costos_reducidos(self, u, v):
        m, n = self.costos.shape
        deltas = np.full((m, n), np.nan)
        for i in range(m):
            for j in range(n):
                if np.isclose(self.asignacion[i, j], 0):
                    if not np.isnan(u[i]) and not np.isnan(v[j]):
                        deltas[i, j] = self.costos[i, j] - u[i] - v[j]
        return deltas

    def _corregir_degeneracion(self):
        m, n = self.costos.shape
        basicas = [(i, j) for i in range(m) for j in range(n)
                   if not np.isclose(self.asignacion[i, j], 0)]
        faltan = (m + n - 1) - len(basicas)
        if faltan <= 0:
            return

        candidatas = sorted(
            [(self.costos[i, j], i, j) for i in range(m) for j in range(n)
             if np.isclose(self.asignacion[i, j], 0)],
            key=lambda x: x[0]
        )
        for _, i, j in candidatas:
            if faltan <= 0:
                break
            if np.isclose(self.asignacion[i, j], 0):
                self.asignacion[i, j] = 0.0
                faltan -= 1

    def _encontrar_ciclo(self, inicio):
        m, n = self.costos.shape
        basicas = [(i, j) for i in range(m) for j in range(n)
                   if not np.isclose(self.asignacion[i, j], 0)]
        return None

    def resolver(self):
        self._vogel_inicial()
        print("=== Solución inicial (VAM) ===")
        print(self.asignacion)
        costo_vam = float(np.sum(self.asignacion * self.costos))
        print(f"Costo VAM: {costo_vam}")

        self.costo_total = costo_vam
        return self.asignacion, self.costo_total


class SolverExacto:

    @staticmethod
    def resolver(modelo: ModeloFlujoCostoMinimo):
        costos = modelo.costos
        oferta = modelo.oferta
        demanda = modelo.demanda
        m, n = costos.shape

        prob = pulp.LpProblem("Transporte", pulp.LpMinimize)
        x = pulp.LpVariable.dicts("x", (range(m), range(n)), lowBound=0, cat="Continuous")

        prob += pulp.lpSum(costos[i][j] * x[i][j] for i in range(m) for j in range(n))

        for i in range(m):
            prob += pulp.lpSum(x[i][j] for j in range(n)) == oferta[i]

        for j in range(n):
            prob += pulp.lpSum(x[i][j] for i in range(m)) == demanda[j]

        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        asignacion = np.zeros((m, n))
        for i in range(m):
            for j in range(n):
                asignacion[i, j] = x[i][j].varValue

        costo = pulp.value(prob.objective)
        return asignacion, costo


class ModeloFactory:

    @staticmethod
    def crear_modelo(tipo, costos, oferta, demanda):
        if tipo == "transporte":
            return ModeloTransporte(costos, oferta, demanda)
        raise ValueError(f"Tipo de modelo no soportado: {tipo}")


if __name__ == "__main__":
    costos = [
        [19, 30, 50, 10],
        [70, 30, 40, 60],
        [40,  8, 70, 20],
    ]
    oferta  = [7, 9, 18]
    demanda = [5, 8, 7, 14]

    modelo = ModeloFactory.crear_modelo("transporte", costos, oferta, demanda)

    asign_vam, costo_vam = modelo.resolver()

    asign_opt, costo_opt = SolverExacto.resolver(modelo)

    print("\n=== Solución óptima (PuLP + CBC) ===")
    print(asign_opt)
    print(f"Costo óptimo: {costo_opt}")
