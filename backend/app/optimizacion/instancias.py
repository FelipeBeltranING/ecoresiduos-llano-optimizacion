import numpy as np

from app.optimizacion.red import RedLogistica

# Caja aproximada del departamento del Meta (latitud, longitud)
LAT_MIN, LAT_MAX = 2.6, 4.9
LON_MIN, LON_MAX = -74.4, -71.1
FACTOR_TORTUOSIDAD = 1.3


def _haversine_matriz(lat1, lon1, lat2, lon2) -> np.ndarray:
    fi1, fi2 = np.radians(lat1)[:, None], np.radians(lat2)[None, :]
    dfi = fi2 - fi1
    dlambda = np.radians(lon2)[None, :] - np.radians(lon1)[:, None]
    a = np.sin(dfi / 2) ** 2 + np.cos(fi1) * np.cos(fi2) * np.sin(dlambda / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


# Instancia sintética reproducible de m empresas y n plantas (HU-14)
def generar_instancia(
    m: int, n: int, semilla: int = 0, costo_km: float = 350, holgura: float = 1.1
) -> RedLogistica:
    rng = np.random.default_rng(semilla)
    lat_e = rng.uniform(LAT_MIN, LAT_MAX, m)
    lon_e = rng.uniform(LON_MIN, LON_MAX, m)
    lat_p = rng.uniform(LAT_MIN, LAT_MAX, n)
    lon_p = rng.uniform(LON_MIN, LON_MAX, n)

    oferta = np.round(rng.uniform(20, 150, m))
    pesos = rng.uniform(0.5, 1.5, n)
    capacidad = np.round(pesos / pesos.sum() * oferta.sum() * holgura)
    operacion = np.round(rng.uniform(38_000, 55_000, n), -2)
    distancias = np.maximum(1.0, _haversine_matriz(lat_e, lon_e, lat_p, lon_p) * FACTOR_TORTUOSIDAD)
    costos = costo_km * distancias + operacion[None, :]

    return RedLogistica(
        codigos_empresas=[f"S{i + 1:03d}" for i in range(m)],
        codigos_plantas=[f"T{j + 1:02d}" for j in range(n)],
        oferta=oferta,
        capacidad=capacidad,
        costos=costos,
        rutas_habilitadas=np.ones((m, n), dtype=bool),
        costo_operacion=operacion,
    )
