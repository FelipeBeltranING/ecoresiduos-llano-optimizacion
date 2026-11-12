"""Reportes en PDF (ReportLab) y Excel (openpyxl) de ejecuciones y análisis (HU-16)."""

import io
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas.analisis import AnalisisSalida
from app.schemas.optimizacion import EjecucionDetalle

VERDE = colors.HexColor("#2F6B3A")
TITULO = "EcoResiduos del Llano · Grupo Orion"


def cop(valor: float | None) -> str:
    if valor is None:
        return "—"
    return "$ " + f"{valor:,.0f}".replace(",", ".")


def num(valor: float | None, decimales: int = 2) -> str:
    if valor is None:
        return "—"
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _tabla(filas: list[list], anchos: list[float] | None = None) -> Table:
    tabla = Table(filas, colWidths=anchos, repeatRows=1)
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), VERDE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#C9D3C4")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5EF")]),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    return tabla


def _grafica_convergencia(puntos: list[tuple[int, float, float]]) -> Drawing:
    dibujo = Drawing(16 * cm, 6 * cm)
    grafica = LinePlot()
    grafica.x, grafica.y = 40, 25
    grafica.width, grafica.height = 16 * cm - 60, 6 * cm - 45
    grafica.data = [[(g, m) for g, m, _ in puntos], [(g, p) for g, _, p in puntos]]
    grafica.lines[0].strokeColor = VERDE
    grafica.lines[1].strokeColor = colors.HexColor("#C8862A")
    grafica.yValueAxis.labelTextFormat = lambda v: f"{v / 1e6:.1f} M"
    dibujo.add(grafica)
    dibujo.add(
        String(45, 6 * cm - 12, "Mejor (verde) y promedio (ocre) por generación", fontSize=8)
    )
    return dibujo


def _documento(contenido: list) -> bytes:
    salida = io.BytesIO()
    documento = SimpleDocTemplate(
        salida, pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm, topMargin=1.5 * cm
    )
    documento.build(contenido)
    return salida.getvalue()


def _encabezado(titulo: str) -> list:
    estilos = getSampleStyleSheet()
    return [
        Paragraph(TITULO, estilos["Normal"]),
        Paragraph(titulo, estilos["Title"]),
        Paragraph(f"Generado el {datetime.now():%Y-%m-%d %H:%M}", estilos["Normal"]),
        Spacer(1, 0.4 * cm),
    ]


# ---------- Ejecución ----------


def pdf_ejecucion(detalle: EjecucionDetalle) -> bytes:
    estilos = getSampleStyleSheet()
    metodo = "Modelo exacto (PuLP + CBC)" if detalle.metodo == "EXACTO" else "Algoritmo Genético"
    contenido = _encabezado(f"Reporte de ejecución · {metodo}")
    contenido.append(
        _tabla(
            [
                ["Campo", "Valor"],
                ["Identificador", str(detalle.id)],
                ["Estado", detalle.estado],
                ["Costo total (COP/semana)", cop(detalle.costo_total)],
                ["Tiempo de cómputo (ms)", num(detalle.tiempo_ms)],
                ["Violaciones de restricciones", num(detalle.violaciones, 4)],
                ["Fecha", f"{detalle.creado_en:%Y-%m-%d %H:%M}"],
            ],
            [6 * cm, 10 * cm],
        )
    )
    contenido += [Spacer(1, 0.4 * cm), Paragraph("Asignación de flujos", estilos["Heading2"])]
    filas = [["Origen", "Destino", "Toneladas", "Costo unitario", "Costo"]]
    for flujo in detalle.flujos:
        filas.append(
            [
                flujo.origen,
                flujo.destino,
                num(flujo.toneladas),
                cop(flujo.costo_unitario),
                cop(flujo.toneladas * flujo.costo_unitario),
            ]
        )
    contenido.append(_tabla(filas))

    if detalle.sensibilidad:
        contenido += [
            Spacer(1, 0.4 * cm),
            Paragraph("Precios sombra, holguras y costos reducidos", estilos["Heading2"]),
        ]
        filas = [["Tipo", "Elemento", "Valor", "Rango inferior", "Rango superior"]]
        for registro in detalle.sensibilidad:
            filas.append(
                [
                    registro.tipo,
                    registro.elemento,
                    num(registro.valor),
                    num(registro.rango_inf),
                    num(registro.rango_sup),
                ]
            )
        contenido.append(_tabla(filas))

    if detalle.convergencia:
        contenido += [Spacer(1, 0.4 * cm), Paragraph("Convergencia del AG", estilos["Heading2"])]
        puntos = [(c.generacion, c.mejor_costo, c.costo_promedio) for c in detalle.convergencia]
        contenido.append(_grafica_convergencia(puntos))
    return _documento(contenido)


def _hoja(libro: Workbook, titulo: str, filas: list[list]) -> None:
    hoja = libro.create_sheet(titulo)
    for fila in filas:
        hoja.append(fila)
    for celda in hoja[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="2F6B3A")
    for columna in hoja.columns:
        ancho = max(len(str(c.value or "")) for c in columna) + 2
        hoja.column_dimensions[columna[0].column_letter].width = min(ancho, 45)


def excel_ejecucion(detalle: EjecucionDetalle) -> bytes:
    libro = Workbook()
    libro.remove(libro.active)
    _hoja(
        libro,
        "Resumen",
        [
            ["Campo", "Valor"],
            ["Identificador", str(detalle.id)],
            ["Método", str(detalle.metodo)],
            ["Estado", detalle.estado],
            ["Costo total (COP/semana)", detalle.costo_total],
            ["Tiempo (ms)", detalle.tiempo_ms],
            ["Violaciones", detalle.violaciones],
            ["Fecha", detalle.creado_en.replace(tzinfo=None)],
        ],
    )
    _hoja(
        libro,
        "Flujos",
        [["Origen", "Destino", "Toneladas", "Costo unitario", "Costo"]]
        + [
            [f.origen, f.destino, f.toneladas, f.costo_unitario, f.toneladas * f.costo_unitario]
            for f in detalle.flujos
        ],
    )
    if detalle.sensibilidad:
        _hoja(
            libro,
            "Sensibilidad",
            [["Tipo", "Elemento", "Valor", "Rango inferior", "Rango superior"]]
            + [
                [s.tipo, s.elemento, s.valor, s.rango_inf, s.rango_sup]
                for s in detalle.sensibilidad
            ],
        )
    if detalle.convergencia:
        _hoja(
            libro,
            "Convergencia",
            [["Generación", "Mejor costo", "Costo promedio"]]
            + [[c.generacion, c.mejor_costo, c.costo_promedio] for c in detalle.convergencia],
        )
    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()


# ---------- Análisis comparativo y de escalabilidad ----------


def pdf_analisis(analisis: AnalisisSalida) -> bytes:
    estilos = getSampleStyleSheet()
    resultado = analisis.resultado or {}
    if analisis.tipo == "COMPARACION":
        contenido = _encabezado("Reporte comparativo · Exacto vs. Algoritmo Genético")
        exacto, ag = resultado.get("exacto", {}), resultado.get("ag", {})
        contenido.append(
            _tabla(
                [
                    ["Métrica", "Modelo exacto", "Algoritmo Genético"],
                    ["Costo (COP/semana)", cop(exacto.get("costo")), cop(ag.get("mejor"))],
                    ["Costo promedio AG", "—", cop(ag.get("promedio"))],
                    ["Desviación estándar AG", "—", cop(ag.get("desviacion"))],
                    ["Gap mejor (%)", "0", num(ag.get("gap_mejor"), 4)],
                    ["Gap promedio (%)", "0", num(ag.get("gap_promedio"), 4)],
                    [
                        "Tiempo (ms)",
                        num(exacto.get("tiempo_ms")),
                        num(ag.get("tiempo_promedio_ms")),
                    ],
                    [
                        "Violaciones",
                        num(exacto.get("violaciones"), 4),
                        num(ag.get("violaciones_max"), 4),
                    ],
                ],
                [6 * cm, 5 * cm, 5 * cm],
            )
        )
        contenido += [Spacer(1, 0.4 * cm), Paragraph("Corridas del AG", estilos["Heading2"])]
        filas = [["Semilla", "Costo", "Gap (%)", "Tiempo (ms)", "Generaciones"]]
        for corrida in ag.get("corridas", []):
            filas.append(
                [
                    corrida["semilla"],
                    cop(corrida["costo"]),
                    num(corrida["gap"], 4),
                    num(corrida["tiempo_ms"]),
                    corrida["generaciones"],
                ]
            )
        contenido.append(_tabla(filas))
        puntos = [
            (p["generacion"], p["mejor"], p["promedio"]) for p in ag.get("convergencia_mejor", [])
        ]
        if puntos:
            contenido += [Spacer(1, 0.4 * cm), _grafica_convergencia(puntos)]
    else:
        contenido = _encabezado("Reporte de escalabilidad · Exacto vs. AG")
        filas = [["Tamaño", "Variables", "Exacto (ms)", "AG (ms)", "Costo exacto", "Gap AG (%)"]]
        for fila in resultado.get("filas", []):
            filas.append(
                [
                    f"{fila['empresas']} x {fila['plantas']}",
                    fila["variables"],
                    num(fila["tiempo_exacto_ms"]),
                    num(fila["tiempo_ag_ms"]),
                    cop(fila["costo_exacto"]),
                    num(fila["gap"], 3),
                ]
            )
        contenido.append(_tabla(filas))
    if "error" in resultado:
        contenido.append(Paragraph(f"Error: {resultado['error']}", estilos["Normal"]))
    return _documento(contenido)


def excel_analisis(analisis: AnalisisSalida) -> bytes:
    libro = Workbook()
    libro.remove(libro.active)
    resultado = analisis.resultado or {}
    if analisis.tipo == "COMPARACION":
        exacto, ag = resultado.get("exacto", {}), resultado.get("ag", {})
        _hoja(
            libro,
            "Resumen",
            [
                ["Métrica", "Modelo exacto", "Algoritmo Genético"],
                ["Costo (COP/semana)", exacto.get("costo"), ag.get("mejor")],
                ["Costo promedio AG", None, ag.get("promedio")],
                ["Desviación estándar AG", None, ag.get("desviacion")],
                ["Gap mejor (%)", 0, ag.get("gap_mejor")],
                ["Gap promedio (%)", 0, ag.get("gap_promedio")],
                ["Tiempo (ms)", exacto.get("tiempo_ms"), ag.get("tiempo_promedio_ms")],
                ["Violaciones", exacto.get("violaciones"), ag.get("violaciones_max")],
            ],
        )
        _hoja(
            libro,
            "Corridas AG",
            [["Semilla", "Costo", "Gap (%)", "Tiempo (ms)", "Violaciones", "Generaciones"]]
            + [
                [
                    c["semilla"],
                    c["costo"],
                    c["gap"],
                    c["tiempo_ms"],
                    c["violaciones"],
                    c["generaciones"],
                ]
                for c in ag.get("corridas", [])
            ],
        )
        _hoja(
            libro,
            "Convergencia",
            [["Generación", "Mejor", "Promedio"]]
            + [
                [p["generacion"], p["mejor"], p["promedio"]]
                for p in ag.get("convergencia_mejor", [])
            ],
        )
    else:
        columnas = [
            "empresas",
            "plantas",
            "variables",
            "costo_exacto",
            "tiempo_exacto_ms",
            "costo_ag",
            "tiempo_ag_ms",
            "gap",
            "violaciones_ag",
            "generaciones_ag",
        ]
        _hoja(
            libro,
            "Escalabilidad",
            [columnas] + [[f.get(c) for c in columnas] for f in resultado.get("filas", [])],
        )
    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()
