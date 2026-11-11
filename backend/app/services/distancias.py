import math

RADIO_TIERRA_KM = 6371.0
# Factor de tortuosidad vial: la carretera es más larga que la línea recta
FACTOR_TORTUOSIDAD = 1.3


# Distancia en línea recta entre dos coordenadas (fórmula de Haversine)
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    fi1 = math.radians(lat1)
    fi2 = math.radians(lat2)
    delta_fi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_fi / 2) ** 2
        + math.cos(fi1) * math.cos(fi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * RADIO_TIERRA_KM * math.asin(math.sqrt(a))


# Distancia vial estimada cuando no hay una distancia medida por carretera
def distancia_vial_estimada(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return round(max(1.0, haversine_km(lat1, lon1, lat2, lon2) * FACTOR_TORTUOSIDAD), 1)
