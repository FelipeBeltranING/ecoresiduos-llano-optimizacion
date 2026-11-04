import numpy as np
import verificar_balanceo.py
def vogel(costos, oferta, demanda):
    """
    Obtiene una solución inicial factible usando el Método de Aproximación
    de Vogel (VAM).

    Parámetros:
    -----------
    costos : list[list] o np.ndarray (m x n) -> matriz de costos unitarios
    oferta : list o np.ndarray (m)           -> oferta de cada origen
    demanda: list o np.ndarray (n)           -> demanda de cada destino

    Retorna:
    --------
    asignacion : np.ndarray (m x n) -> matriz con las cantidades asignadas
    costo_total: float              -> costo total de la solución inicial
    """
    # 1) Verificar / balancear usando la función anterior
    balanceado, oferta, demanda = verificar_balanceo(oferta, demanda)

    costos = np.array(costos, dtype=float)

    # Si se agregó un destino ficticio, agregamos una columna de ceros
    if costos.shape[1] < len(demanda):
        costos = np.hstack([costos, np.zeros((costos.shape[0], 1))])
    # Si se agregó un origen ficticio, agregamos una fila de ceros
    if costos.shape[0] < len(oferta):
        costos = np.vstack([costos, np.zeros((1, costos.shape[1]))])

    m, n = costos.shape
    oferta = oferta.copy()
    demanda = demanda.copy()
    asignacion = np.zeros((m, n), dtype=float)

    filas_activas = list(range(m))
    columnas_activas = list(range(n))

    # 2) Iterar hasta agotar ofertas y demandas
    while filas_activas and columnas_activas:
        # Calcular penalizaciones por fila (solo columnas activas)
        pen_filas = []
        for i in filas_activas:
            valores = sorted(costos[i, columnas_activas])
            if len(valores) >= 2:
                pen_filas.append((valores[1] - valores[0], i))
            else:
                pen_filas.append((0.0, i))

        # Calcular penalizaciones por columna (solo filas activas)
        pen_cols = []
        for j in columnas_activas:
            valores = sorted(costos[filas_activas, j])
            if len(valores) >= 2:
                pen_cols.append((valores[1] - valores[0], j))
            else:
                pen_cols.append((0.0, j))

        # Elegir la mayor penalización (empate -> primera encontrada)
        max_pen_fila = max(pen_filas, key=lambda x: x[0])
        max_pen_col = max(pen_cols, key=lambda x: x[0])

        if max_pen_fila[0] >= max_pen_col[0]:
            i = max_pen_fila[1]
            # Celda de menor costo en esa fila (entre columnas activas)
            j = min(columnas_activas, key=lambda c: costos[i, c])
        else:
            j = max_pen_col[1]
            # Celda de menor costo en esa columna (entre filas activas)
            i = min(filas_activas, key=lambda f: costos[f, j])

        # Asignar la mayor cantidad posible
        cantidad = min(oferta[i], demanda[j])
        asignacion[i, j] = cantidad
        oferta[i] -= cantidad
        demanda[j] -= cantidad

        # Eliminar fila o columna agotada
        if np.isclose(oferta[i], 0):
            filas_activas.remove(i)
        if np.isclose(demanda[j], 0):
            columnas_activas.remove(j)

    costo_total = float(np.sum(asignacion * costos))

    print("\n--- Matriz de asignación (solución inicial VAM) ---")
    print(asignacion)
    print(f"\nCosto total de la solución inicial: {costo_total}")

    return asignacion, costo_total


# =========================================================
# Ejemplo de uso
# =========================================================
if __name__ == "__main__":
    # Matriz de costos (3 orígenes x 4 destinos)
    costos = [
        [19, 30, 50, 10],
        [70, 30, 40, 60],
        [40,  8, 70, 20],
    ]
    oferta  = [7, 9, 18]
    demanda = [5, 8, 7, 14]

    asignacion, costo = vogel(costos, oferta, demanda)
