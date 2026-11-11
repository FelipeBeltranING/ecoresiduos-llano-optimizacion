# AlgoritmoGenetico

import numpy as np

class Individuo:
    def __init__(self, flujos: np.ndarray):
        # El cromosoma se almacena como matriz bidimensional m x n 
        self.cromosoma = flujos 
        self.fitness = 0.0
        self.costo_total = 0.0
        self.violaciones = 0.0

class InicializadorAG:
    def __init__(self, oferta: np.ndarray, capacidad: np.ndarray, matriz_costos: np.ndarray, semilla: int = None):
        self.a = oferta      
        self.b = capacidad     
        self.C = matriz_costos
        self.m = len(oferta)
        self.n = len(capacidad)
        self.rng = np.random.default_rng(semilla) 
        
    def generar_individuo_dirichlet(self) -> Individuo:
        # Cromosoma aleatorio.
        flujos = np.zeros((self.m, self.n))
        for i in range(self.m):
            proporciones = self.rng.dirichlet(np.ones(self.n))
            flujos[i, :] = proporciones * self.a[i]
        return Individuo(flujos)

    def generar_individuo_heuristico(self) -> Individuo:
        # Cromosoma heurística de costo mínimo.
        flujos = np.zeros((self.m, self.n))
        oferta_restante = np.copy(self.a)
        capacidad_restante = np.copy(self.b)
        
        # Iterar sobre las rutas ordenadas
        rutas_ordenadas = np.dstack(np.unravel_index(np.argsort(self.C.ravel()), (self.m, self.n)))[0]
        
        for i, j in rutas_ordenadas:
            if oferta_restante[i] > 0 and capacidad_restante[j] > 0:
                cantidad = min(oferta_restante[i], capacidad_restante[j])
                flujos[i, j] = cantidad
                oferta_restante[i] -= cantidad
                capacidad_restante[j] -= cantidad
                
        for i in range(self.m):
            if oferta_restante[i] > 0:
                flujos[i, :] += oferta_restante[i] / self.n 
                
        return Individuo(flujos)

    def crear_poblacion_inicial(self, tam_poblacion: int = 100) -> list[Individuo]:
        # Crea la población inicial con la proporción 90% aleatoria / 10% heurística.
        num_heuristico = int(tam_poblacion * 0.10)
        num_aleatorio = tam_poblacion - num_heuristico
        
        poblacion = []
        for _ in range(num_heuristico):
            poblacion.append(self.generar_individuo_heuristico())
            
        for _ in range(num_aleatorio):
            poblacion.append(self.generar_individuo_dirichlet())
            
        return poblacion
    
class EvaluadorAG:
    def __init__(self, oferta: np.ndarray, capacidad: np.ndarray, matriz_costos: np.ndarray, lambda_pen: float = 1e6):
        self.a = oferta        
        self.b = capacidad     
        self.C = matriz_costos 
        self.lambda_pen = lambda_pen 

    def reparar_cromosoma(self, flujos: np.ndarray) -> np.ndarray:
        # Reescala cada fila para que la suma coincida con la oferta
        flujos_reparados = np.copy(flujos)
        m, n = flujos_reparados.shape
        
        for i in range(m):
            suma_fila = np.sum(flujos_reparados[i, :])
            if suma_fila > 0:
                flujos_reparados[i, :] = flujos_reparados[i, :] * (self.a[i] / suma_fila)
            else:
                flujos_reparados[i, :] = self.a[i] / n
                
        return flujos_reparados

    def evaluar(self, individuo) -> None:
        # Calcula el costo Z, penaliza las violaciones y asigna el fitness
        individuo.cromosoma = self.reparar_cromosoma(individuo.cromosoma)
        
        # Costo total 
        individuo.costo_total = np.sum(individuo.cromosoma * self.C)

        oferta_asignada = np.sum(individuo.cromosoma, axis=1)
        capacidad_usada = np.sum(individuo.cromosoma, axis=0)
        
        violacion_oferta = np.sum(np.abs(oferta_asignada - self.a))
        
        violacion_capacidad = np.sum(np.maximum(0, capacidad_usada - self.b))
        
        individuo.violaciones = violacion_oferta + violacion_capacidad
        
        # Fitness 
        denominador = individuo.costo_total + (self.lambda_pen * individuo.violaciones)
        individuo.fitness = 1.0 / (denominador + 1e-10)
        
class OperadoresGeneticos:
    def __init__(self, rng_seed: int = None):
        self.rng = np.random.default_rng(rng_seed)

    def seleccion_torneo(self, poblacion: list, k: int = 3):
        torneo = self.rng.choice(poblacion, k, replace=False)
        mejor = max(torneo, key=lambda ind: ind.fitness)
        return type(mejor)(np.copy(mejor.cromosoma))

    def seleccion_ruleta(self, poblacion: list):
        fitness_total = sum(ind.fitness for ind in poblacion)
        probabilidades = [ind.fitness / fitness_total for ind in poblacion]
        elegido = self.rng.choice(poblacion, p=probabilidades)
        return type(elegido)(np.copy(elegido.cromosoma))

    def cruce_un_punto(self, padre1, padre2):
        m, _ = padre1.cromosoma.shape
        punto = self.rng.integers(1, m)
        
        hijo1_cromosoma = np.vstack((padre1.cromosoma[:punto, :], padre2.cromosoma[punto:, :]))
        hijo2_cromosoma = np.vstack((padre2.cromosoma[:punto, :], padre1.cromosoma[punto:, :]))
        
        return type(padre1)(hijo1_cromosoma), type(padre2)(hijo2_cromosoma)

    def mutar_transferencia(self, individuo):
        m, n = individuo.cromosoma.shape
        i = self.rng.integers(0, m) 
        j, j_prima = self.rng.choice(n, 2, replace=False) 
        
        flujo_actual = individuo.cromosoma[i, j]
        if flujo_actual > 0:
            fraccion = self.rng.random() * flujo_actual
            individuo.cromosoma[i, j] -= fraccion
            individuo.cromosoma[i, j_prima] += fraccion