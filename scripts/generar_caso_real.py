"""Genera el caso real del Meta (HU-19) a partir de fuentes públicas.

Fuentes:
- Evaluaciones Agropecuarias Municipales (EVA), MinAgricultura/UPRA, datos.gov.co (2pnw-mmge):
  producción 2018 de palma de aceite (aceite crudo) y arroz (paddy verde) por municipio.
- Inventario bovino y bufalino por ciclo de vacunación, FNG/ICA, datos.gov.co (cea5-4ctf):
  vigencia 2025, ciclo I.
- DIVIPOLA, DANE, datos.gov.co (gdxc-w37w): coordenadas de los municipios.
- OSRM sobre OpenStreetMap (router.project-osrm.org): distancia vial y trazado de cada ruta.

Uso (desde la raíz del repositorio, con internet):

    python scripts/generar_caso_real.py

Escribe backend/app/services/datos/caso_real_meta.json y caso_base_geometrias.json.
Solo usa la biblioteca estándar. Las peticiones a OSRM se espacian para respetar el
servidor de demostración.
"""

import json
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "backend" / "app" / "services" / "datos"
AGENTE = "ecoresiduos-llano-optimizacion/1.0 (proyecto academico)"
SOCRATA = "https://www.datos.gov.co/resource"
OSRM = "https://router.project-osrm.org"

TASA_EXTRACCION_ACEITE = 0.21
TUSA_POR_RFF = 0.22
CASCARILLA_POR_PADDY = 0.20
ESTIERCOL_KG_DIA = 10.0

CAPTACION = {"PALMA": 0.065, "ARROZ": 0.25, "BOVINO": 0.005}

FUENTES = [
    ("R01", "PALMA", "PUERTO GAITÁN", "Núcleo palmero de Puerto Gaitán", "Palma (tusa/raquis)"),
    ("R02", "PALMA", "SAN CARLOS DE GUAROA", "Núcleo palmero de San Carlos de Guaroa",
     "Palma (tusa/raquis)"),
    ("R03", "PALMA", "ACACÍAS", "Núcleo palmero de Acacías", "Palma (tusa/raquis)"),
    ("R04", "PALMA", "CABUYARO", "Núcleo palmero de Cabuyaro", "Palma (tusa/raquis)"),
    ("R05", "PALMA", "BARRANCA DE UPÍA", "Núcleo palmero de Barranca de Upía",
     "Palma (tusa/raquis)"),
    ("R06", "PALMA", "SAN MARTÍN", "Núcleo palmero de San Martín", "Palma (tusa/raquis)"),
    ("R07", "ARROZ", "FUENTE DE ORO", "Molinos arroceros de Fuente de Oro", "Arroz (cascarilla)"),
    ("R08", "ARROZ", "PUERTO LÓPEZ", "Molinos arroceros de Puerto López", "Arroz (cascarilla)"),
    ("R09", "ARROZ", "VILLAVICENCIO", "Molinos arroceros de Villavicencio", "Arroz (cascarilla)"),
    ("R10", "BOVINO", "PUERTO LÓPEZ", "Ganaderías de Puerto López", "Ganadería (estiércol)"),
    ("R11", "BOVINO", "SAN MARTÍN", "Ganaderías de San Martín", "Ganadería (estiércol)"),
    ("R12", "BOVINO", "VILLAVICENCIO", "Ganaderías de Villavicencio", "Ganadería (estiércol)"),
]

PLANTAS = [
    ("RP1", "VILLAVICENCIO", "Planta Villavicencio", 300, 45000),
    ("RP2", "RESTREPO", "Planta Restrepo", 180, 52000),
    ("RP3", "GRANADA", "Planta Granada", 250, 48000),
    ("RP4", "PUERTO GAITÁN", "Planta Puerto Gaitán", 220, 40000),
]


def nombre_bonito(municipio: str) -> str:
    return municipio.title().replace(" De ", " de ")


DISTANCIA_MINIMA_KM = 5.0


def normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(sin_tildes.upper().replace("VISTA HERMOSA", "VISTAHERMOSA").split())


def obtener_json(url: str):
    peticion = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(peticion, timeout=60) as respuesta:
        return json.loads(respuesta.read().decode("utf-8"))


def socrata(recurso: str, **parametros) -> list[dict]:
    consulta = urllib.parse.urlencode(parametros)
    return obtener_json(f"{SOCRATA}/{recurso}.json?{consulta}")


def numero(texto: str | None) -> float:
    if texto in (None, ""):
        return 0.0
    return float(str(texto).replace(",", "."))


def coordenadas_municipios() -> dict[str, tuple[float, float]]:
    filas = socrata("gdxc-w37w", cod_dpto="50", **{"$limit": 50})
    return {
        normalizar(f["nom_mpio"]): (numero(f["latitud"]), numero(f["longitud"])) for f in filas
    }


def produccion_eva() -> dict[tuple[str, str], float]:
    filas = socrata(
        "2pnw-mmge",
        **{
            "$where": "upper(departamento)='META' AND a_o='2018' AND "
            "cultivo in('PALMA DE ACEITE','ARROZ')",
            "$limit": 1000,
        },
    )
    total: dict[tuple[str, str], float] = {}
    for fila in filas:
        tipo = "PALMA" if fila["cultivo"] == "PALMA DE ACEITE" else "ARROZ"
        clave = (tipo, normalizar(fila["municipio"]))
        total[clave] = total.get(clave, 0.0) + numero(fila.get("producci_n_t"))
    return total


def inventario_bovino() -> dict[str, float]:
    filas = socrata(
        "cea5-4ctf",
        **{
            "$where": "upper(departamento)='META' AND vigencia='2025' AND ciclo='Ciclo I'",
            "$limit": 100,
        },
    )
    return {normalizar(f["municipio"]): numero(f["total_bovinos_pm"]) for f in filas}


def residuo_anual(tipo: str, produccion: float) -> float:
    if tipo == "PALMA":
        return produccion / TASA_EXTRACCION_ACEITE * TUSA_POR_RFF
    if tipo == "ARROZ":
        return produccion * CASCARILLA_POR_PADDY
    return produccion * ESTIERCOL_KG_DIA * 365 / 1000


def osrm_ruta(origen: tuple[float, float], destino: tuple[float, float]) -> dict:
    coordenadas = f"{origen[1]},{origen[0]};{destino[1]},{destino[0]}"
    url = f"{OSRM}/route/v1/driving/{coordenadas}?overview=simplified&geometries=polyline"
    datos = obtener_json(url)
    if datos.get("code") != "Ok":
        raise RuntimeError(f"OSRM: {datos.get('code')} {datos.get('message')}")
    ruta = datos["routes"][0]
    return {
        "distancia_km": max(DISTANCIA_MINIMA_KM, round(ruta["distance"] / 1000, 1)),
        "duracion_min": round(ruta["duration"] / 60, 1),
        "geometria": ruta["geometry"],
    }


def generar_caso_real(coordenadas: dict) -> dict:
    eva = produccion_eva()
    bovinos = inventario_bovino()
    empresas = []
    for codigo, tipo, municipio, nombre, tipo_residuo in FUENTES:
        clave = normalizar(municipio)
        if tipo == "BOVINO":
            produccion = bovinos[clave]
            unidad = "cabezas (ICA/FNG 2025, ciclo I)"
        else:
            produccion = eva[(tipo, clave)]
            unidad = "t aceite crudo (EVA 2018)" if tipo == "PALMA" else "t paddy verde (EVA 2018)"
        anual = residuo_anual(tipo, produccion)
        oferta = round(anual / 52 * CAPTACION[tipo], 1)
        lat, lon = coordenadas[clave]
        empresas.append(
            {
                "codigo": codigo,
                "nombre": nombre,
                "municipio": nombre_bonito(municipio),
                "tipo_residuo": tipo_residuo,
                "oferta_t": oferta,
                "latitud": lat,
                "longitud": lon,
                "fuente_dato": {
                    "produccion": produccion,
                    "unidad": unidad,
                    "residuo_anual_t": round(anual, 1),
                    "captacion": CAPTACION[tipo],
                },
            }
        )

    plantas = []
    for codigo, municipio, nombre, capacidad, operacion in PLANTAS:
        lat, lon = coordenadas[normalizar(municipio)]
        plantas.append(
            {
                "codigo": codigo,
                "nombre": nombre,
                "municipio": nombre_bonito(municipio),
                "capacidad_t": capacidad,
                "costo_operacion_t": operacion,
                "latitud": lat,
                "longitud": lon,
            }
        )

    rutas = []
    for empresa in empresas:
        for planta in plantas:
            datos = osrm_ruta(
                (empresa["latitud"], empresa["longitud"]), (planta["latitud"], planta["longitud"])
            )
            rutas.append({"origen": empresa["codigo"], "destino": planta["codigo"], **datos})
            time.sleep(0.4)

    return {
        "descripcion": "Caso real del Meta: producción EVA 2018, inventario bovino ICA/FNG 2025, "
        "coordenadas DIVIPOLA y distancias viales OSRM sobre OpenStreetMap",
        "coeficientes": {
            "tasa_extraccion_aceite": TASA_EXTRACCION_ACEITE,
            "tusa_por_rff": TUSA_POR_RFF,
            "cascarilla_por_paddy": CASCARILLA_POR_PADDY,
            "estiercol_kg_dia": ESTIERCOL_KG_DIA,
            "captacion": CAPTACION,
        },
        "empresas": empresas,
        "plantas": plantas,
        "rutas": rutas,
    }


def geometrias_caso_base() -> list[dict]:
    import sys

    sys.path.insert(0, str(RAIZ / "backend"))
    from app.services.caso_base_datos import EMPRESAS, PLANTAS as PLANTAS_BASE  # noqa: E402

    geometrias = []
    for empresa in EMPRESAS:
        for planta in PLANTAS_BASE:
            datos = osrm_ruta(
                (empresa["latitud"], empresa["longitud"]), (planta["latitud"], planta["longitud"])
            )
            geometrias.append(
                {
                    "origen": empresa["codigo"],
                    "destino": planta["codigo"],
                    "distancia_osrm_km": datos["distancia_km"],
                    "geometria": datos["geometria"],
                }
            )
            time.sleep(0.4)
    return geometrias


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    coordenadas = coordenadas_municipios()
    caso = generar_caso_real(coordenadas)
    (SALIDA / "caso_real_meta.json").write_text(
        json.dumps(caso, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"Caso real: {len(caso['empresas'])} empresas, oferta "
          f"{sum(e['oferta_t'] for e in caso['empresas']):.1f} t/semana")
    geometrias = geometrias_caso_base()
    (SALIDA / "caso_base_geometrias.json").write_text(
        json.dumps(geometrias, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"Geometrías del caso base: {len(geometrias)}")


if __name__ == "__main__":
    main()
