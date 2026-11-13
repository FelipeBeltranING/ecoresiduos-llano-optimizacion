
import numpy as np
from typing import Dict, Any, List
from scipy.optimize import linprog


def analizar_sensibilidad_costos(
    c: np.ndarray,
    A_eq: np.ndarray,
    b_eq: np.ndarray,
    bounds: List[tuple],
    rango_variacion: float = 0.20,
    pasos: int = 10
) -> Dict[str, Any]:
    res_base = linprog(c=c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if not res_base.success:
        raise ValueError("El problema base de optimización no tiene solución factible.")
    
    costo_base = res_base.fun
    solucion_base = res_base.x

    resultados_sensibilidad = {
        "costo_base": float(costo_base),
        "variaciones_evaluadas": []
    }

    factores = np.linspace(1 - rango_variacion, 1 + rango_variacion, pasos)

    for i, c_i_original in enumerate(c):
        curva_impacto = []
        
        for factor in factores:
            c_modificado = c.copy()
            c_modificado[i] = c_i_original * factor
            
            res_var = linprog(c=c_modificado, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            
            if res_var.success:
                curva_impacto.append({
                    "factor": round(float(factor), 2),
                    "nuevo_costo_unitario": float(c_modificado[i]),
                    "costo_total_sistema": float(res_var.fun),
                    "variacion_porcentual_total": float(((res_var.fun - costo_base) / costo_base) * 100)
                })
        
        resultados_sensibilidad["variaciones_evaluadas"].append({
            "indice_ruta": i,
            "costo_original": float(c_i_original),
            "sensibilidad": curva_impacto
        })

    return resultados_sensibilidad
