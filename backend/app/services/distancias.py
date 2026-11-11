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


FUENTE_OSRM = "OSRM"
FUENTE_ESTIMADA = "ESTIMADA"
FUENTE_MANUAL = "MANUAL"
DISTANCIA_MINIMA_KM = 5.0


# Ruta vial real con OSRM sobre OpenStreetMap; None si el servicio no responde
def ruta_osrm(lat1: float, lon1: float, lat2: float, lon2: float) -> dict | None:
    import json
    import urllib.request

    from app.core.config import settings

    if not settings.osrm_habilitado:
        return None
    url = (
        f"{settings.osrm_url}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
        "?overview=simplified&geometries=polyline"
    )
    peticion = urllib.request.Request(url, headers={"User-Agent": "ecoresiduos-llano/1.0"})
    try:
        with urllib.request.urlopen(peticion, timeout=8) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
    except Exception:  # noqa: BLE001 - sin red se usa la estimación
        return None
    if datos.get("code") != "Ok" or not datos.get("routes"):
        return None
    ruta = datos["routes"][0]
    return {
        "distancia_km": max(DISTANCIA_MINIMA_KM, round(ruta["distance"] / 1000, 1)),
        "duracion_min": round(ruta["duration"] / 60, 1),
        "geometria": ruta["geometry"],
    }


# Distancia vial de una ruta nueva: OSRM si está disponible, si no Haversine x 1,3
def medir_ruta(lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
    real = ruta_osrm(lat1, lon1, lat2, lon2)
    if real is not None:
        return {**real, "fuente_distancia": FUENTE_OSRM}
    return {
        "distancia_km": distancia_vial_estimada(lat1, lon1, lat2, lon2),
        "duracion_min": None,
        "geometria": None,
        "fuente_distancia": FUENTE_ESTIMADA,
    }
