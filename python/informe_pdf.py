"""Informe PDF automatico (reportlab): parametros, indicadores, graficas y conclusiones."""
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from reportlab.lib.utils import ImageReader

AZUL = colors.HexColor("#1f5fa8")
GRIS_CLARO = colors.HexColor("#eef2f7")


def _fmt(v, unidad=""):
    if isinstance(v, bool):
        return "Sí" if v else "No"
    if isinstance(v, (int, float)):
        if v != 0 and (abs(v) < 1e-3 or abs(v) >= 1e6):
            s = f"{v:.3e}"
        elif float(v).is_integer():
            s = f"{int(v)}"
        else:
            s = f"{v:.3f}".rstrip("0").rstrip(".")
        return f"{s} {unidad}".strip()
    return str(v)


def _tabla(filas, encabezado, anchos, estilos):
    data = [[Paragraph(f"<b>{h}</b>", estilos["celda_h"]) for h in encabezado]]
    for fila in filas:
        data.append([Paragraph(str(c), estilos["celda"]) for c in fila])
    t = Table(data, colWidths=anchos, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c4d4")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def _imagen(ruta, ancho_max):
    w, h = ImageReader(ruta).getSize()
    esc = ancho_max / w
    return Image(ruta, width=w * esc, height=h * esc)


def generar_pdf(ruta, titulo_tema, etiquetas_param, entrada, indicadores, graficas,
                conclusiones, modelo_texto):
    base = getSampleStyleSheet()
    est = {
        "titulo": ParagraphStyle("t", parent=base["Title"], textColor=AZUL, fontSize=20, leading=24),
        "sub": ParagraphStyle("s", parent=base["Normal"], fontSize=10.5, textColor=colors.HexColor("#444444")),
        "h": ParagraphStyle("h", parent=base["Heading2"], textColor=AZUL, spaceBefore=12, spaceAfter=6, keepWithNext=1),
        "n": ParagraphStyle("n", parent=base["Normal"], fontSize=10, leading=14),
        "celda": ParagraphStyle("c", parent=base["Normal"], fontSize=9, leading=11),
        "celda_h": ParagraphStyle("ch", parent=base["Normal"], fontSize=9, leading=11, textColor=colors.white),
        "cap": ParagraphStyle("cap", parent=base["Italic"], fontSize=8.5, textColor=colors.HexColor("#555555"), alignment=1),
        "viñeta": ParagraphStyle("v", parent=base["Normal"], fontSize=10, leading=14, leftIndent=14, bulletIndent=2, spaceAfter=4),
    }
    meta = entrada.get("meta", {})
    ahora = meta.get("fecha") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def pie(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(2 * cm, 1.2 * cm, "Simulador educativo de Física · Programación de Computadores")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(ruta, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=2 * cm,
                            title=f"Informe de simulación - {titulo_tema}",
                            author=meta.get("equipo") or "Simulador educativo de Física")
    ancho = A4[0] - 4 * cm
    el = [Paragraph("Informe de simulación", est["titulo"]),
          Paragraph(f"<b>Tema:</b> {titulo_tema}", est["sub"]),
          Paragraph(f"<b>Escenario:</b> {entrada.get('escenario', 'Personalizado')}", est["sub"]),
          Paragraph(f"<b>Fecha de ejecución:</b> {ahora}", est["sub"])]
    if meta.get("equipo"):
        el.append(Paragraph(f"<b>Equipo:</b> {meta['equipo']}", est["sub"]))
    el.append(Paragraph("<b>Flujo:</b> Java (captura, validación y JSON) → Python (cálculo, "
                        "indicadores, gráficas) → PDF", est["sub"]))

    el.append(Paragraph("1. Parámetros utilizados", est["h"]))
    filas = [(etq, _fmt(entrada["parametros"][k], u)) for k, (etq, u) in etiquetas_param.items()
             if k in entrada["parametros"]]
    el.append(_tabla(filas, ["Parámetro", "Valor"], [ancho * 0.65, ancho * 0.35], est))

    el.append(Paragraph("2. Resultados e indicadores", est["h"]))
    filas = [(i["etiqueta"], _fmt(i["valor"], i["unidad"])) for i in indicadores]
    el.append(_tabla(filas, ["Indicador", "Valor"], [ancho * 0.65, ancho * 0.35], est))

    el.append(Paragraph("3. Gráficas", est["h"]))
    for titulo, ruta_img, cap in graficas:
        el.append(KeepTogether([Paragraph(f"<b>{titulo}</b>", est["n"]),
                                _imagen(ruta_img, ancho * 0.92),
                                Paragraph(cap, est["cap"]), Spacer(1, 8)]))

    el.append(Paragraph("4. Conclusiones", est["h"]))
    for c in conclusiones:
        el.append(Paragraph(c, est["viñeta"], bulletText="•"))

    el.append(Paragraph("5. Modelo físico empleado", est["h"]))
    for linea in modelo_texto:
        el.append(Paragraph(linea, est["n"]))
    doc.build(el, onFirstPage=pie, onLaterPages=pie)
    return ruta
