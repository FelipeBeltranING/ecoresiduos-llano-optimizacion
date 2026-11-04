"""AlgoritmoGenetico"""

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
        self.a = oferta        # Vector de oferta (m,)
        self.b = capacidad     # Vector de capacidad (n,)
        self.C = matriz_costos # Matriz de costos unitarios (m x n)
        self.m = len(oferta)
        self.n = len(capacidad)
        self.rng = np.random.default_rng(semilla) 
        
    def generar_individuo_dirichlet(self) -> Individuo:
        """Genera un cromosoma aleatorio."""
        flujos = np.zeros((self.m, self.n))
        for i in range(self.m):
            proporciones = self.rng.dirichlet(np.ones(self.n))
            flujos[i, :] = proporciones * self.a[i]
        return Individuo(flujos)

    def generar_individuo_heuristico(self) -> Individuo:
        """Genera un cromosoma usando la heurística de costo mínimo."""
        flujos = np.zeros((self.m, self.n))
        oferta_restante = np.copy(self.a)
        capacidad_restante = np.copy(self.b)
        
        # Iterar sobre las rutas ordenadas de menor a mayor costo
        rutas_ordenadas = np.dstack(np.unravel_index(np.argsort(self.C.ravel()), (self.m, self.n)))[0]
        
        for i, j in rutas_ordenadas:
            if oferta_restante[i] > 0 and capacidad_restante[j] > 0:
                cantidad = min(oferta_restante[i], capacidad_restante[j])
                flujos[i, j] = cantidad
                oferta_restante[i] -= cantidad
                capacidad_restante[j] -= cantidad
                
        # la penalización del fitness se encargará de castigar esta solución más adelante.
        for i in range(self.m):
            if oferta_restante[i] > 0:
                flujos[i, :] += oferta_restante[i] / self.n 
                
        return Individuo(flujos)

    def crear_poblacion_inicial(self, tam_poblacion: int = 100) -> list[Individuo]:
        """Crea la población inicial con la proporción 90% aleatoria / 10% heurística."""
        num_heuristico = int(tam_poblacion * 0.10)
        num_aleatorio = tam_poblacion - num_heuristico
        
        poblacion = []
        for _ in range(num_heuristico):
            poblacion.append(self.generar_individuo_heuristico())
            
        for _ in range(num_aleatorio):
            poblacion.append(self.generar_individuo_dirichlet())
            
        return poblacion