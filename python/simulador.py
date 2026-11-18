#!/usr/bin/env python3
"""Procesamiento de la simulacion (parte Python del proyecto).

Uso:  python3 simulador.py --entrada entrada.json --salida carpeta_salida

Lee el JSON generado por Java, calcula la simulacion, produce indicadores, graficas (PNG),
un resultados.json y el informe PDF. La ultima linea de stdout es un JSON de estado que
Java lee para saber que archivos se generaron.
"""
import argparse
import json
import math
import os
import sys

import analisis
import fisica_caida
import fisica_tiro
import graficas
import informe_pdf

TEMAS = {
    "tiro_parabolico": "Tiro parabólico",
    "caida_energia": "Caída libre y conservación de la energía",
}

ETIQUETAS = {
    "tiro_parabolico": {
        "v0": ("Rapidez inicial", "m/s"), "angulo": ("Ángulo de lanzamiento", "°"),
        "h0": ("Altura inicial", "m"), "g": ("Gravedad", "m/s²"), "masa": ("Masa", "kg"),
        "usar_arrastre": ("Resistencia del aire", ""), "cd": ("Coeficiente de arrastre Cd", ""),
        "area": ("Área frontal", "m²")},
    "caida_energia": {
        "h0": ("Altura inicial", "m"), "v0": ("Velocidad inicial (+ hacia arriba)", "m/s"),
        "masa": ("Masa", "kg"), "g": ("Gravedad", "m/s²"),
        "e": ("Coeficiente de restitución e", ""), "rebotes": ("Rebotes a simular", "")},
}

MODELOS = {
    "tiro_parabolico": [
        "Sin aire: x(t) = v0·cos(θ)·t ; y(t) = h0 + v0·sin(θ)·t − ½·g·t². El movimiento "
        "horizontal es uniforme y el vertical uniformemente acelerado.",
        "Con aire: se añade una fuerza de arrastre cuadrática F = −k·|v|·v con "
        "k = ½·ρ·Cd·A (ρ = 1.225 kg/m³). Las ecuaciones se integran numéricamente con "
        "Runge-Kutta de 4.º orden (paso 1 ms).",
        "Energías: Ec = ½·m·v² ; Ep = m·g·y ; Em = Ec + Ep. Sin aire, Em es constante.",
    ],
    "caida_energia": [
        "Movimiento vertical con aceleración constante: y(t) = h0 + v0·t − ½·g·t² ; "
        "v(t) = v0 − g·t.",
        "Conservación de la energía: ½·m·v² + m·g·y = constante, de donde la rapidez de "
        "impacto es v = √(v0² + 2·g·h0).",
        "Rebotes: en cada choque con el suelo la rapidez se multiplica por el coeficiente de "
        "restitución e, así que la energía mecánica se multiplica por e² y la altura máxima "
        "de cada tramo también.",
    ],
}


def _error(msg, codigo=2):
    print(json.dumps({"estado": "error", "mensaje": msg}, ensure_ascii=False))
    sys.exit(codigo)


def _numero(params, clave, minimo=None, maximo=None):
    if clave not in params:
        _error(f"Falta el parámetro '{clave}' en el JSON de entrada.")
    v = params[clave]
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        _error(f"El parámetro '{clave}' debe ser un número finito.")
    if minimo is not None and v < minimo:
        _error(f"El parámetro '{clave}' no puede ser menor que {minimo}.")
    if maximo is not None and v > maximo:
        _error(f"El parámetro '{clave}' no puede ser mayor que {maximo}.")
    return float(v)


def validar_defensivo(data):
    """Segunda barrera de validacion (la principal esta en Java)."""
    tema = data.get("tema")
    if tema not in TEMAS:
        _error(f"Tema desconocido: {tema!r}.")
    pr = data.get("parametros")
    if not isinstance(pr, dict):
        _error("El JSON no contiene el objeto 'parametros'.")
    p = {}
    p["g"] = _numero(pr, "g", 0.1)
    p["masa"] = _numero(pr, "masa", 1e-6)
    p["h0"] = _numero(pr, "h0", 0)
    if tema == "tiro_parabolico":
        p["v0"] = _numero(pr, "v0", 0)
        p["angulo"] = _numero(pr, "angulo", 0, 90)
        arr = pr.get("usar_arrastre", False)
        if not isinstance(arr, bool):
            _error("'usar_arrastre' debe ser true o false.")
        p["usar_arrastre"] = arr
        p["cd"] = _numero(pr, "cd", 0)
        p["area"] = _numero(pr, "area", 0)
        if arr and (p["cd"] <= 0 or p["area"] <= 0):
            _error("Con resistencia del aire, Cd y el área deben ser mayores que cero.")
    else:
        p["v0"] = _numero(pr, "v0")
        p["e"] = _numero(pr, "e", 0, 1)
        r = _numero(pr, "rebotes", 0, 50)
        if int(r) != r:
            _error("'rebotes' debe ser un número entero.")
        p["rebotes"] = int(r)
    return tema, p


def ejecutar(entrada_path, salida_dir):
    try:
        with open(entrada_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as ex:
        _error(f"No se pudo leer el JSON de entrada: {ex}")
    tema, p = validar_defensivo(data)
    os.makedirs(salida_dir, exist_ok=True)

    try:
        if tema == "tiro_parabolico":
            ideal = fisica_tiro.simular_ideal(p)
            sim = fisica_tiro.simular_arrastre(p) if p["usar_arrastre"] else ideal
            b_main = fisica_tiro.barrido_angulos(p, p["usar_arrastre"])
            b_ideal = fisica_tiro.barrido_angulos(p, False) if p["usar_arrastre"] else b_main
            ind = analisis.indicadores_tiro(p, sim, ideal, b_main)
            concl = analisis.conclusiones_tiro(p, ind, sim)
            grafs = graficas.graficas_tiro(salida_dir, p, sim, ideal, b_main, b_ideal)
        else:
            sim = fisica_caida.simular(p)
            ind = analisis.indicadores_caida(p, sim)
            concl = analisis.conclusiones_caida(p, ind, sim)
            grafs = graficas.graficas_caida(salida_dir, p, sim)
    except (ValueError, RuntimeError) as ex:
        _error(str(ex))

    pdf = informe_pdf.generar_pdf(os.path.join(salida_dir, "informe.pdf"), TEMAS[tema],
                                  ETIQUETAS[tema], dict(data, parametros=dict(data["parametros"])),
                                  ind, grafs, concl, MODELOS[tema])
    resultados = {"tema": tema, "escenario": data.get("escenario", "Personalizado"),
                  "parametros": data["parametros"], "indicadores": ind, "conclusiones": concl}
    ruta_res = os.path.join(salida_dir, "resultados.json")
    with open(ruta_res, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    return {"estado": "ok", "directorio": os.path.abspath(salida_dir), "pdf": os.path.abspath(pdf),
            "resultados": os.path.abspath(ruta_res),
            "grafica_principal": os.path.abspath(grafs[0][1]),
            "graficas": [os.path.abspath(g[1]) for g in grafs]}


def main():
    ap = argparse.ArgumentParser(description="Procesa una simulación de Física.")
    ap.add_argument("--entrada", required=True, help="JSON generado por Java")
    ap.add_argument("--salida", required=True, help="carpeta donde se escriben los resultados")
    args = ap.parse_args()
    print(json.dumps(ejecutar(args.entrada, args.salida), ensure_ascii=False))


if __name__ == "__main__":
    main()
