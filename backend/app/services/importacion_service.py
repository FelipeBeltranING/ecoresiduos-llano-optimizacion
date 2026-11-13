import io

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, aliased

from app.db.models import Nodo, ParametroGlobal, Ruta, TipoNodo
from app.schemas.gestion import ErrorImportacion, NodoEntrada, ResumenImportacion

COLUMNAS_NODO = [
    "codigo",
    "nombre",
    "municipio",
    "tipo_residuo",
    "oferta_t",
    "capacidad_t",
    "costo_operacion_t",
    "latitud",
    "longitud",
    "activo",
]
COLUMNAS_RUTA = ["origen", "destino", "distancia_km", "costo_km_t", "habilitada"]
COLUMNAS_PARAMETRO = ["clave", "valor", "unidad", "descripcion"]
HOJAS_NODO = {"Empresas": TipoNodo.FUENTE, "Plantas": TipoNodo.PLANTA, "Acopios": TipoNodo.ACOPIO}


def escribir_hoja(libro: Workbook, titulo: str, columnas: list[str], filas: list[list]) -> None:
    hoja = libro.create_sheet(titulo)
    hoja.append(columnas)
    for celda in hoja[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="2F6B3A")
    for fila in filas:
        hoja.append(fila)
    for columna in hoja.columns:
        ancho = max(len(str(c.value or "")) for c in columna) + 2
        hoja.column_dimensions[columna[0].column_letter].width = min(ancho, 40)


def exportar_red(sesion: Session) -> bytes:
    libro = Workbook()
    libro.remove(libro.active)

    for titulo, tipo in HOJAS_NODO.items():
        filas = []
        consulta = select(Nodo).where(Nodo.tipo == tipo).order_by(Nodo.codigo)
        for nodo in sesion.execute(consulta).scalars():
            filas.append(
                [
                    nodo.codigo,
                    nodo.nombre,
                    nodo.municipio,
                    nodo.tipo_residuo,
                    None if nodo.oferta_t is None else float(nodo.oferta_t),
                    None if nodo.capacidad_t is None else float(nodo.capacidad_t),
                    float(nodo.costo_operacion_t),
                    float(nodo.latitud),
                    float(nodo.longitud),
                    nodo.activo,
                ]
            )
        escribir_hoja(libro, titulo, COLUMNAS_NODO, filas)

    origen = aliased(Nodo)
    destino = aliased(Nodo)
    consulta = (
        select(Ruta, origen.codigo, destino.codigo)
        .join(origen, Ruta.origen_id == origen.id)
        .join(destino, Ruta.destino_id == destino.id)
        .order_by(origen.codigo, destino.codigo)
    )
    filas = []
    for ruta, codigo_origen, codigo_destino in sesion.execute(consulta):
        filas.append(
            [
                codigo_origen,
                codigo_destino,
                None if ruta.distancia_km is None else float(ruta.distancia_km),
                None if ruta.costo_km_t is None else float(ruta.costo_km_t),
                ruta.habilitada,
            ]
        )
    escribir_hoja(libro, "Rutas", COLUMNAS_RUTA, filas)

    filas = [
        [p.clave, float(p.valor), p.unidad, p.descripcion]
        for p in sesion.execute(select(ParametroGlobal).order_by(ParametroGlobal.clave)).scalars()
    ]
    escribir_hoja(libro, "Parametros", COLUMNAS_PARAMETRO, filas)

    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()


def leer_filas(hoja) -> list[tuple[int, dict]]:
    filas = list(hoja.iter_rows(values_only=True))
    if not filas:
        return []
    encabezados = [str(c).strip().lower() if c is not None else "" for c in filas[0]]
    resultado = []
    for numero, valores in enumerate(filas[1:], start=2):
        if all(v is None or str(v).strip() == "" for v in valores):
            continue
        resultado.append((numero, dict(zip(encabezados, valores, strict=False))))
    return resultado


def a_booleano(valor, por_defecto: bool = True) -> bool:
    if valor is None or str(valor).strip() == "":
        return por_defecto
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() in ("1", "true", "si", "sí", "verdadero", "x")


def mensaje_validacion(error: ValidationError) -> str:
    partes = []
    for detalle in error.errors():
        campo = ".".join(str(p) for p in detalle["loc"]) or "fila"
        partes.append(f"{campo}: {detalle['msg']}")
    return "; ".join(partes)


def importar_red(sesion: Session, contenido: bytes) -> ResumenImportacion:
    try:
        libro = load_workbook(io.BytesIO(contenido), data_only=True)
    except Exception:
        return ResumenImportacion(
            importado=False,
            errores=[
                ErrorImportacion(hoja="-", fila=0, mensaje="El archivo no es un Excel válido")
            ],
        )

    errores: list[ErrorImportacion] = []
    nodos: list[tuple[NodoEntrada, bool]] = []
    codigos_archivo: set[str] = set()

    for titulo, tipo in HOJAS_NODO.items():
        if titulo not in libro.sheetnames:
            continue
        for numero, fila in leer_filas(libro[titulo]):
            datos = {c: fila.get(c) for c in COLUMNAS_NODO if fila.get(c) not in (None, "")}
            datos["codigo"] = str(datos.get("codigo", "")).strip().upper()
            datos["tipo"] = tipo
            try:
                entrada = NodoEntrada(**{k: v for k, v in datos.items() if k != "activo"})
            except ValidationError as error:
                errores.append(
                    ErrorImportacion(hoja=titulo, fila=numero, mensaje=mensaje_validacion(error))
                )
                continue
            if entrada.codigo in codigos_archivo:
                errores.append(
                    ErrorImportacion(
                        hoja=titulo, fila=numero, mensaje=f"Código repetido: {entrada.codigo}"
                    )
                )
                continue
            codigos_archivo.add(entrada.codigo)
            nodos.append((entrada, a_booleano(fila.get("activo"))))

    codigos_base = {c for (c,) in sesion.execute(select(Nodo.codigo))}
    codigos_validos = codigos_base | codigos_archivo
    rutas = []
    if "Rutas" in libro.sheetnames:
        for numero, fila in leer_filas(libro["Rutas"]):
            origen = str(fila.get("origen") or "").strip().upper()
            destino = str(fila.get("destino") or "").strip().upper()
            problema = None
            if origen not in codigos_validos or destino not in codigos_validos:
                problema = f"Ruta {origen}->{destino}: el origen o el destino no existe"
            elif origen == destino:
                problema = "El origen y el destino deben ser distintos"
            distancia = fila.get("distancia_km")
            costo_km = fila.get("costo_km_t")
            try:
                distancia = None if distancia in (None, "") else float(distancia)
                costo_km = None if costo_km in (None, "") else float(costo_km)
            except (TypeError, ValueError):
                problema = "La distancia y el costo por t·km deben ser números"
            if problema is None and distancia is not None and distancia <= 0:
                problema = "La distancia debe ser mayor que cero"
            if problema is None and costo_km is not None and costo_km < 0:
                problema = "El costo por t·km no puede ser negativo"
            if problema:
                errores.append(ErrorImportacion(hoja="Rutas", fila=numero, mensaje=problema))
                continue
            rutas.append((origen, destino, distancia, costo_km, a_booleano(fila.get("habilitada"))))

    parametros = []
    if "Parametros" in libro.sheetnames:
        for numero, fila in leer_filas(libro["Parametros"]):
            clave = str(fila.get("clave") or "").strip()
            try:
                valor = float(fila.get("valor"))
            except (TypeError, ValueError):
                errores.append(
                    ErrorImportacion(hoja="Parametros", fila=numero, mensaje="Valor no numérico")
                )
                continue
            if sesion.get(ParametroGlobal, clave) is None:
                errores.append(
                    ErrorImportacion(
                        hoja="Parametros", fila=numero, mensaje=f"Parámetro desconocido: {clave}"
                    )
                )
                continue
            parametros.append((clave, valor))

    if errores:
        return ResumenImportacion(importado=False, errores=errores)

    try:
        for entrada, activo in nodos:
            datos = entrada.model_dump()
            datos["activo"] = activo
            sentencia = insert(Nodo).values(**datos)
            actualizar = {k: v for k, v in datos.items() if k != "codigo"}
            sesion.execute(
                sentencia.on_conflict_do_update(index_elements=["codigo"], set_=actualizar)
            )
        sesion.flush()
        ids = {c: i for c, i in sesion.execute(select(Nodo.codigo, Nodo.id))}
        for origen, destino, distancia, costo_km, habilitada in rutas:
            valores = {
                "origen_id": ids[origen],
                "destino_id": ids[destino],
                "distancia_km": distancia,
                "costo_km_t": costo_km,
                "habilitada": habilitada,
            }
            sentencia = insert(Ruta).values(**valores)
            sesion.execute(
                sentencia.on_conflict_do_update(
                    index_elements=["origen_id", "destino_id"],
                    set_={k: v for k, v in valores.items() if k not in ("origen_id", "destino_id")},
                )
            )
        for clave, valor in parametros:
            sesion.get(ParametroGlobal, clave).valor = valor
        sesion.commit()
    except Exception:
        sesion.rollback()
        raise

    return ResumenImportacion(
        importado=True,
        empresas=sum(1 for e, _ in nodos if e.tipo == TipoNodo.FUENTE),
        plantas=sum(1 for e, _ in nodos if e.tipo == TipoNodo.PLANTA),
        acopios=sum(1 for e, _ in nodos if e.tipo == TipoNodo.ACOPIO),
        rutas=len(rutas),
    )
