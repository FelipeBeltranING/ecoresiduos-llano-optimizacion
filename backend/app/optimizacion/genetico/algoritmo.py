
import numpy as np


class Recursos:
    def __init__(self, n_caminos: int, recursos: np.ndarray = None):
        self.matriz = recursos
        self.n = n_caminos

    def de(self, camino: int) -> np.ndarray:
        if self.matriz is None:
            return np.array([camino])
        return np.flatnonzero(self.matriz[:, camino])

    def uso(self, flujo_por_camino: np.ndarray) -> np.ndarray:
        if self.matriz is None:
            return flujo_por_camino
        return self.matriz.astype(float) @ flujo_por_camino

    def caminos_que_usan(self, recurso: int) -> np.ndarray:
        if self.matriz is None:
            return np.array([recurso])
        return np.flatnonzero(self.matriz[recurso])


class Individuo:
    def __init__(self, flujos: np.ndarray):
        self.cromosoma = flujos
        self.fitness = 0.0
        self.costo_total = 0.0
        self.violaciones = 0.0
        self.evaluado = False

    def copiar(self) -> "Individuo":
        copia = Individuo(np.copy(self.cromosoma))
        copia.fitness = self.fitness
        copia.costo_total = self.costo_total
        copia.violaciones = self.violaciones
        copia.evaluado = self.evaluado
        return copia


class InicializadorAG:
    def __init__(
        self,
        oferta: np.ndarray,
        capacidad: np.ndarray,
        matriz_costos: np.ndarray,
        semilla: int = None,
        habilitadas: np.ndarray = None,
        recursos: np.ndarray = None,
    ):
        self.a = oferta
        self.b = capacidad
        self.C = matriz_costos
        self.m = len(oferta)
        self.n = matriz_costos.shape[1]
        self.recursos = Recursos(self.n, recursos)
        if habilitadas is None:
            habilitadas = np.ones((self.m, self.n), dtype=bool)
        self.habilitadas = habilitadas
        self.rng = np.random.default_rng(semilla)

    def generar_individuo_dirichlet(self) -> Individuo:
        flujos = np.zeros((self.m, self.n))
        for i in range(self.m):
            columnas = np.flatnonzero(self.habilitadas[i])
            proporciones = self.rng.dirichlet(np.ones(len(columnas)))
            flujos[i, columnas] = proporciones * self.a[i]
        return Individuo(flujos)

    def generar_individuo_heuristico(self) -> Individuo:
        flujos = np.zeros((self.m, self.n))
        oferta_restante = np.copy(self.a)
        capacidad_restante = np.copy(self.b)

        ruido = self.rng.random(self.C.shape) * 1e-6
        costos = np.where(self.habilitadas, self.C + ruido, np.inf)
        rutas_ordenadas = np.dstack(np.unravel_index(np.argsort(costos.ravel()), (self.m, self.n)))[0]

        for i, j in rutas_ordenadas:
            if not self.habilitadas[i, j]:
                continue
            usados = self.recursos.de(j)
            cupo = capacidad_restante[usados].min()
            if oferta_restante[i] > 0 and cupo > 0:
                cantidad = min(oferta_restante[i], cupo)
                flujos[i, j] = cantidad
                oferta_restante[i] -= cantidad
                capacidad_restante[usados] -= cantidad

        for i in range(self.m):
            if oferta_restante[i] > 0:
                columnas = np.flatnonzero(self.habilitadas[i])
                flujos[i, columnas] += oferta_restante[i] / len(columnas)

        return Individuo(flujos)

    def crear_poblacion_inicial(self, tam_poblacion: int = 100) -> list[Individuo]:
        num_heuristico = max(1, int(tam_poblacion * 0.10))
        num_aleatorio = tam_poblacion - num_heuristico

        poblacion = []
        for _ in range(num_heuristico):
            poblacion.append(self.generar_individuo_heuristico())

        for _ in range(num_aleatorio):
            poblacion.append(self.generar_individuo_dirichlet())

        return poblacion


class EvaluadorAG:
    def __init__(
        self,
        oferta: np.ndarray,
        capacidad: np.ndarray,
        matriz_costos: np.ndarray,
        lambda_pen: float = 1e6,
        habilitadas: np.ndarray = None,
        recursos: np.ndarray = None,
    ):
        self.a = oferta
        self.b = capacidad
        self.C = matriz_costos
        self.lambda_pen = lambda_pen
        self.recursos = Recursos(matriz_costos.shape[1], recursos)
        if habilitadas is None:
            habilitadas = np.ones(matriz_costos.shape, dtype=bool)
        self.habilitadas = habilitadas
        costos = np.where(self.habilitadas, self.C, np.inf)
        self.orden_por_costo = np.argsort(costos, axis=1)

    def reparar_cromosoma(self, flujos: np.ndarray) -> np.ndarray:
        flujos_reparados = np.where(self.habilitadas, np.maximum(flujos, 0.0), 0.0)
        m, n = flujos_reparados.shape

        suma_filas = flujos_reparados.sum(axis=1)
        con_flujo = suma_filas > 0
        flujos_reparados[con_flujo] *= (self.a[con_flujo] / suma_filas[con_flujo])[:, None]
        for i in np.flatnonzero(~con_flujo):
            columnas = np.flatnonzero(self.habilitadas[i])
            flujos_reparados[i, columnas] = self.a[i] / len(columnas)

        usada = self.recursos.uso(flujos_reparados.sum(axis=0))
        for r in np.flatnonzero(usada > self.b + 1e-9):
            exceso = usada[r] - self.b[r]
            for j in self.recursos.caminos_que_usan(r):
                filas = np.flatnonzero(flujos_reparados[:, j] > 0)
                filas = sorted(filas, key=lambda i, j=j: self._costo_alternativo(i, j, r, usada))
                for i in filas:
                    if exceso <= 1e-9:
                        break
                    for destino in self.orden_por_costo[i]:
                        if exceso <= 1e-9 or flujos_reparados[i, j] <= 1e-12:
                            break
                        if not self._es_alternativa(i, destino, r):
                            continue
                        cupo = self._cupo(destino, usada)
                        if cupo <= 1e-9:
                            continue
                        mover = min(cupo, exceso, flujos_reparados[i, j])
                        flujos_reparados[i, j] -= mover
                        flujos_reparados[i, destino] += mover
                        usada[self.recursos.de(j)] -= mover
                        usada[self.recursos.de(destino)] += mover
                        exceso -= mover

        return flujos_reparados

    def _es_alternativa(self, i: int, destino: int, recurso: int) -> bool:
        if not self.habilitadas[i, destino]:
            return False
        return recurso not in self.recursos.de(destino)

    def _cupo(self, camino: int, usada: np.ndarray) -> float:
        usados = self.recursos.de(camino)
        return float((self.b[usados] - usada[usados]).min())

    def _costo_alternativo(self, i: int, j: int, recurso: int, usada: np.ndarray) -> float:
        for destino in self.orden_por_costo[i]:
            if self._es_alternativa(i, destino, recurso) and self._cupo(destino, usada) > 0:
                return self.C[i, destino] - self.C[i, j]
        return np.inf

    def evaluar(self, individuo) -> None:
        individuo.cromosoma = self.reparar_cromosoma(individuo.cromosoma)

        individuo.costo_total = float(np.sum(individuo.cromosoma * self.C))

        oferta_asignada = np.sum(individuo.cromosoma, axis=1)
        capacidad_usada = self.recursos.uso(np.sum(individuo.cromosoma, axis=0))

        violacion_oferta = np.sum(np.abs(oferta_asignada - self.a))

        violacion_capacidad = np.sum(np.maximum(0, capacidad_usada - self.b))

        individuo.violaciones = float(violacion_oferta + violacion_capacidad)

        denominador = individuo.costo_total + (self.lambda_pen * individuo.violaciones)
        individuo.fitness = 1.0 / (denominador + 1e-10)
        individuo.evaluado = True


class OperadoresGeneticos:
    def __init__(self, rng_seed: int = None, habilitadas: np.ndarray = None):
        self.rng = np.random.default_rng(rng_seed)
        self.habilitadas = habilitadas

    def seleccion_torneo(self, poblacion: list, k: int = 3):
        indices = self.rng.choice(len(poblacion), min(k, len(poblacion)), replace=False)
        mejor = max((poblacion[i] for i in indices), key=lambda ind: ind.fitness)
        return Individuo(np.copy(mejor.cromosoma))

    def seleccion_ruleta(self, poblacion: list):
        fitness = np.array([ind.fitness for ind in poblacion])
        probabilidades = fitness / fitness.sum()
        elegido = poblacion[self.rng.choice(len(poblacion), p=probabilidades)]
        return Individuo(np.copy(elegido.cromosoma))

    def cruce_un_punto(self, padre1, padre2):
        m, _ = padre1.cromosoma.shape
        if m < 2:
            return Individuo(np.copy(padre1.cromosoma)), Individuo(np.copy(padre2.cromosoma))
        punto = self.rng.integers(1, m)

        hijo1_cromosoma = np.vstack((padre1.cromosoma[:punto, :], padre2.cromosoma[punto:, :]))
        hijo2_cromosoma = np.vstack((padre2.cromosoma[:punto, :], padre1.cromosoma[punto:, :]))

        return Individuo(hijo1_cromosoma), Individuo(hijo2_cromosoma)

    def cruce_dos_puntos(self, padre1, padre2):
        m, _ = padre1.cromosoma.shape
        if m < 3:
            return self.cruce_un_punto(padre1, padre2)
        punto1, punto2 = sorted(self.rng.choice(np.arange(1, m), 2, replace=False))

        hijo1_cromosoma = np.copy(padre1.cromosoma)
        hijo2_cromosoma = np.copy(padre2.cromosoma)
        hijo1_cromosoma[punto1:punto2, :] = padre2.cromosoma[punto1:punto2, :]
        hijo2_cromosoma[punto1:punto2, :] = padre1.cromosoma[punto1:punto2, :]

        return Individuo(hijo1_cromosoma), Individuo(hijo2_cromosoma)

    def mutar_transferencia(self, individuo):
        m, n = individuo.cromosoma.shape
        if n < 2:
            return
        i = self.rng.integers(0, m)
        origenes = np.flatnonzero(individuo.cromosoma[i] > 0)
        if len(origenes) == 0:
            return
        j = self.rng.choice(origenes)
        destinos = [d for d in range(n) if d != j]
        if self.habilitadas is not None:
            destinos = [d for d in destinos if self.habilitadas[i, d]]
        if not destinos:
            return
        j_prima = self.rng.choice(destinos)

        fraccion = self.rng.random() * individuo.cromosoma[i, j]
        individuo.cromosoma[i, j] -= fraccion
        individuo.cromosoma[i, j_prima] += fraccion
        individuo.evaluado = False


class MotorAG:
    def __init__(self, inicializador, evaluador, operadores):
        self.inicializador = inicializador
        self.evaluador = evaluador
        self.operadores = operadores
        self.historial: list[tuple[int, float, float]] = []

    def ejecutar(
        self,
        tam_poblacion: int = 100,
        generaciones: int = 300,
        tasa_cruce: float = 0.85,
        tasa_mutacion: float = 0.10,
        tipo_seleccion: str = "torneo",
        tipo_cruce: str = "un_punto",
        elitismo: int = 2,
        paciencia: int = 50,
    ):
        self.historial = []
        poblacion = self.inicializador.crear_poblacion_inicial(tam_poblacion)
        for ind in poblacion:
            self.evaluador.evaluar(ind)

        mejor_historico = None
        generaciones_sin_mejora = 0

        for gen in range(generaciones):
            poblacion.sort(key=lambda ind: ind.fitness, reverse=True)
            costos = [ind.costo_total + self.evaluador.lambda_pen * ind.violaciones for ind in poblacion]
            self.historial.append((gen, float(costos[0]), float(np.mean(costos))))

            if mejor_historico is None or poblacion[0].fitness > mejor_historico.fitness:
                mejor_historico = poblacion[0].copiar()
                generaciones_sin_mejora = 0
            else:
                generaciones_sin_mejora += 1

            if generaciones_sin_mejora >= paciencia:
                break

            nueva_poblacion = [ind.copiar() for ind in poblacion[:elitismo]]

            while len(nueva_poblacion) < tam_poblacion:
                if tipo_seleccion == "torneo":
                    padre1 = self.operadores.seleccion_torneo(poblacion)
                    padre2 = self.operadores.seleccion_torneo(poblacion)
                else:
                    padre1 = self.operadores.seleccion_ruleta(poblacion)
                    padre2 = self.operadores.seleccion_ruleta(poblacion)

                if self.operadores.rng.random() < tasa_cruce:
                    if tipo_cruce == "dos_puntos":
                        hijo1, hijo2 = self.operadores.cruce_dos_puntos(padre1, padre2)
                    else:
                        hijo1, hijo2 = self.operadores.cruce_un_punto(padre1, padre2)
                else:
                    hijo1 = Individuo(np.copy(padre1.cromosoma))
                    hijo2 = Individuo(np.copy(padre2.cromosoma))

                if self.operadores.rng.random() < tasa_mutacion:
                    self.operadores.mutar_transferencia(hijo1)
                if self.operadores.rng.random() < tasa_mutacion:
                    self.operadores.mutar_transferencia(hijo2)

                self.evaluador.evaluar(hijo1)
                self.evaluador.evaluar(hijo2)
                nueva_poblacion.extend([hijo1, hijo2])

            poblacion = nueva_poblacion[:tam_poblacion]

        return mejor_historico
