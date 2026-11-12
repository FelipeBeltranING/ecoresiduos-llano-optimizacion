# Empresas agropecuarias del caso base del Meta
EMPRESAS = [
    {
        "codigo": "E01",
        "nombre": "Palmas del Upía",
        "municipio": "Barranca de Upía",
        "tipo_residuo": "Palma (raquis, fibra)",
        "oferta_t": 120,
        "latitud": 4.567,
        "longitud": -72.966,
    },
    {
        "codigo": "E02",
        "nombre": "Arrocera Llano Verde",
        "municipio": "Puerto López",
        "tipo_residuo": "Arroz (cascarilla)",
        "oferta_t": 95,
        "latitud": 4.085,
        "longitud": -72.956,
    },
    {
        "codigo": "E03",
        "nombre": "Ganadería San Martín",
        "municipio": "San Martín",
        "tipo_residuo": "Ganadería (estiércol)",
        "oferta_t": 80,
        "latitud": 3.696,
        "longitud": -73.699,
    },
    {
        "codigo": "E04",
        "nombre": "Agroindustrial Guaroa",
        "municipio": "San Carlos de Guaroa",
        "tipo_residuo": "Palma (raquis, fibra)",
        "oferta_t": 140,
        "latitud": 3.711,
        "longitud": -73.243,
    },
    {
        "codigo": "E05",
        "nombre": "Molino Acacías",
        "municipio": "Acacías",
        "tipo_residuo": "Arroz (cascarilla)",
        "oferta_t": 70,
        "latitud": 3.987,
        "longitud": -73.765,
    },
    {
        "codigo": "E06",
        "nombre": "Hacienda Cumaral",
        "municipio": "Cumaral",
        "tipo_residuo": "Ganadería (estiércol)",
        "oferta_t": 60,
        "latitud": 4.27,
        "longitud": -73.487,
    },
    {
        "codigo": "E07",
        "nombre": "Forestal Cabuyaro",
        "municipio": "Cabuyaro",
        "tipo_residuo": "Forestal (aserrín, corteza)",
        "oferta_t": 85,
        "latitud": 4.287,
        "longitud": -72.792,
    },
    {
        "codigo": "E08",
        "nombre": "Agrícola Castilla",
        "municipio": "Castilla La Nueva",
        "tipo_residuo": "Arroz (cascarilla)",
        "oferta_t": 75,
        "latitud": 3.829,
        "longitud": -73.688,
    },
    {
        "codigo": "E09",
        "nombre": "Palmeras Fuente de Oro",
        "municipio": "Fuente de Oro",
        "tipo_residuo": "Palma (raquis, fibra)",
        "oferta_t": 110,
        "latitud": 3.462,
        "longitud": -73.62,
    },
    {
        "codigo": "E10",
        "nombre": "Agropecuaria Lejanías",
        "municipio": "Lejanías",
        "tipo_residuo": "Ganadería y cacao",
        "oferta_t": 55,
        "latitud": 3.527,
        "longitud": -74.023,
    },
]

# Plantas de procesamiento del caso base
PLANTAS = [
    {
        "codigo": "P01",
        "nombre": "Planta Villavicencio",
        "municipio": "Villavicencio",
        "capacidad_t": 300,
        "costo_operacion_t": 45000,
        "latitud": 4.142,
        "longitud": -73.627,
    },
    {
        "codigo": "P02",
        "nombre": "Planta Restrepo",
        "municipio": "Restrepo",
        "capacidad_t": 180,
        "costo_operacion_t": 52000,
        "latitud": 4.258,
        "longitud": -73.562,
    },
    {
        "codigo": "P03",
        "nombre": "Planta Granada",
        "municipio": "Granada",
        "capacidad_t": 250,
        "costo_operacion_t": 48000,
        "latitud": 3.546,
        "longitud": -73.707,
    },
    {
        "codigo": "P04",
        "nombre": "Planta Puerto Gaitán",
        "municipio": "Puerto Gaitán",
        "capacidad_t": 220,
        "costo_operacion_t": 40000,
        "latitud": 4.314,
        "longitud": -72.083,
    },
]

# Distancias en km: por cada empresa, la distancia a P01, P02, P03 y P04
DISTANCIAS_KM = {
    "E01": [110, 98, 290, 300],
    "E02": [85, 98, 225, 105],
    "E03": [70, 85, 110, 255],
    "E04": [90, 103, 140, 185],
    "E05": [28, 43, 152, 218],
    "E06": [30, 18, 210, 220],
    "E07": [95, 85, 270, 160],
    "E08": [50, 65, 140, 230],
    "E09": [160, 175, 22, 340],
    "E10": [210, 225, 38, 400],
}

ORDEN_PLANTAS = ["P01", "P02", "P03", "P04"]

# Centros de acopio del caso con nodos de paso (HU-17): Puerto López y San Martín, sobre las vías
# hacia Puerto Gaitán y Granada (coordenadas de la cabecera municipal, DIVIPOLA)
ACOPIOS = [
    {
        "codigo": "A01",
        "nombre": "Acopio Puerto López",
        "municipio": "Puerto López",
        "capacidad_t": 200,
        "costo_operacion_t": 8000,
        "latitud": 4.085,
        "longitud": -72.956,
    },
    {
        "codigo": "A02",
        "nombre": "Acopio San Martín",
        "municipio": "San Martín",
        "capacidad_t": 200,
        "costo_operacion_t": 8000,
        "latitud": 3.696,
        "longitud": -73.699,
    },
]

# Flete consolidado acopio → planta en COP/t·km (tractomula), frente a 350 del flete directo
COSTO_KM_CONSOLIDADO = 200
