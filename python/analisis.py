"""Indicadores y conclusiones automaticas a partir de los resultados de la simulacion."""
import math
import numpy as np

REFERENCIAS_G = {"la Tierra": 9.81, "la Luna": 1.62, "Marte": 3.71,
                 "Venus": 8.87, "Jupiter": 24.79}


def _f(x):
    return float(x)


def _ind(lista, clave, etiqueta, valor, unidad):
    lista.append({"clave": clave, "etiqueta": etiqueta, "valor": _f(valor), "unidad": unidad})


def cuerpo_celeste(g):
    for nombre, ref in REFERENCIAS_G.items():
        if abs(g - ref) / ref <= 0.015:
            return nombre.replace("Jupiter", "Júpiter")
    return None


# ----------------------------------------------------------------- Tema 1
def indicadores_tiro(p, sim, ideal, barrido):
    ang, alc, ang_opt, alc_opt = barrido
    out = []
    t, x, y, vx, vy = sim["t"], sim["x"], sim["y"], sim["vx"], sim["vy"]
    i_max = int(np.argmax(y))
    em0 = sim["em"][0]
    ec_f = sim["ec"][-1]
    _ind(out, "alcance", "Alcance horizontal", x[-1], "m")
    _ind(out, "altura_max", "Altura máxima (sobre el suelo)", y[i_max], "m")
    _ind(out, "t_vuelo", "Tiempo de vuelo", t[-1], "s")
    _ind(out, "t_altura_max", "Tiempo hasta la altura máxima", t[i_max], "s")
    _ind(out, "v_impacto", "Rapidez al impactar", math.hypot(vx[-1], vy[-1]), "m/s")
    _ind(out, "ang_impacto", "Ángulo de impacto (bajo la horizontal)",
         math.degrees(math.atan2(-vy[-1], vx[-1])), "°")
    _ind(out, "em_inicial", "Energía mecánica inicial", em0, "J")
    _ind(out, "ec_final", "Energía cinética al impactar", ec_f, "J")
    _ind(out, "e_disipada", "Energía disipada", em0 - ec_f, "J")
    _ind(out, "pct_disipada", "Energía disipada (% de la inicial)",
         max(0.0, 100.0 * (em0 - ec_f) / em0) if em0 > 0 else 0.0, "%")
    if p["usar_arrastre"]:
        _ind(out, "alcance_ideal", "Alcance sin aire (referencia)", ideal["x"][-1], "m")
        _ind(out, "reduccion_alcance", "Reducción del alcance por el aire",
             100.0 * (1 - x[-1] / ideal["x"][-1]), "%")
    _ind(out, "angulo_optimo", "Ángulo de máximo alcance (en estas condiciones)", ang_opt, "°")
    _ind(out, "alcance_optimo", "Alcance con el ángulo óptimo", alc_opt, "m")
    _ind(out, "eficiencia_angulo", "Alcance logrado vs. alcance óptimo",
         100.0 * x[-1] / alc_opt, "%")
    return out


def conclusiones_tiro(p, ind, sim):
    d = {i["clave"]: i["valor"] for i in ind}
    c = []
    cuerpo = cuerpo_celeste(p["g"])
    lugar = f" (gravedad similar a la de {cuerpo})" if cuerpo else ""
    c.append(f"Con v0 = {p['v0']:.1f} m/s, ángulo de {p['angulo']:.1f}° y altura inicial "
             f"de {p['h0']:.1f} m, con g = {p['g']:.2f} m/s²{lugar}, el proyectil recorre "
             f"{d['alcance']:.2f} m en {d['t_vuelo']:.2f} s y alcanza una altura máxima de "
             f"{d['altura_max']:.2f} m.")
    c.append("El movimiento horizontal es uniforme y el vertical uniformemente acelerado: "
             "ambos son independientes. Por eso el tiempo de vuelo depende solo de la "
             "componente vertical de la velocidad y de la altura inicial.")
    if p["usar_arrastre"]:
        c.append(f"La resistencia del aire reduce el alcance en {d['reduccion_alcance']:.1f} % "
                 f"respecto al caso ideal ({d['alcance_ideal']:.2f} m) y disipa "
                 f"{d['e_disipada']:.1f} J ({d['pct_disipada']:.1f} % de la energía inicial): "
                 "la energía mecánica ya no se conserva y la trayectoria deja de ser simétrica.")
    else:
        c.append("Sin resistencia del aire la energía mecánica se conserva: la energía "
                 "cinética y la potencial se intercambian y su suma permanece constante "
                 f"({d['em_inicial']:.1f} J).")
    if abs(p["angulo"] - d["angulo_optimo"]) <= 1.0:
        c.append(f"El ángulo elegido está prácticamente en el óptimo ({d['angulo_optimo']:.0f}°): "
                 "se logra el máximo alcance posible con esta rapidez.")
    else:
        c.append(f"Para estas condiciones el alcance máximo se obtendría con "
                 f"{d['angulo_optimo']:.0f}° ({d['alcance_optimo']:.2f} m); con el ángulo "
                 f"usado se logra el {d['eficiencia_angulo']:.1f} % de ese alcance.")
    if p["h0"] == 0 and not p["usar_arrastre"]:
        c.append(f"Al lanzar desde el suelo sin aire, ángulos complementarios "
                 f"({p['angulo']:.0f}° y {90 - p['angulo']:.0f}°) dan el mismo alcance, y el "
                 "máximo se da a 45°. Compruébelo en la gráfica de alcance vs. ángulo.")
    elif p["h0"] > 0 and not p["usar_arrastre"]:
        c.append("Al lanzar desde una altura mayor que cero, el ángulo óptimo es menor que "
                 "45°, y la rapidez de impacto es mayor que la de lanzamiento.")
    return c


# ----------------------------------------------------------------- Tema 2
def indicadores_caida(p, sim):
    out = []
    tr = sim["tramos"]
    m, g = p["masa"], p["g"]
    v_teo = math.sqrt(p["v0"] ** 2 + 2 * g * p["h0"])
    v1 = tr[0]["v_impacto"]
    em0 = sim["em"][0]
    emf = sim["em"][-1]
    _ind(out, "t_primer_impacto", "Tiempo hasta el primer impacto", tr[0]["t_impacto"], "s")
    _ind(out, "v_primer_impacto", "Rapidez en el primer impacto", v1, "m/s")
    _ind(out, "v_teorica", "Rapidez por conservación de energía √(v0²+2gh)", v_teo, "m/s")
    _ind(out, "error_energia", "Diferencia relativa (simulación vs. teoría)",
         abs(v1 - v_teo) / v_teo * 100 if v_teo else 0.0, "%")
    _ind(out, "altura_max", "Altura máxima alcanzada", np.max(sim["y"]), "m")
    _ind(out, "em_inicial", "Energía mecánica inicial", em0, "J")
    _ind(out, "ec_primer_impacto", "Energía cinética en el primer impacto", tr[0]["ec_impacto"], "J")
    _ind(out, "n_rebotes", "Rebotes simulados", len(tr) - 1, "")
    _ind(out, "em_final", "Energía mecánica al final de la simulación", emf, "J")
    _ind(out, "pct_disipada", "Energía disipada (% de la inicial)",
         max(0.0, 100.0 * (em0 - emf) / em0) if em0 > 0 else 0.0, "%")
    _ind(out, "t_total", "Duración total simulada", sim["t"][-1], "s")
    return out


def conclusiones_caida(p, ind, sim):
    d = {i["clave"]: i["valor"] for i in ind}
    c = []
    cuerpo = cuerpo_celeste(p["g"])
    lugar = f" (gravedad similar a la de {cuerpo})" if cuerpo else ""
    sentido = ("se suelta" if p["v0"] == 0 else
               f"se lanza hacia {'arriba' if p['v0'] > 0 else 'abajo'} a {abs(p['v0']):.1f} m/s")
    c.append(f"Un objeto de {p['masa']:.2f} kg {sentido} desde {p['h0']:.1f} m con "
             f"g = {p['g']:.2f} m/s²{lugar}. Llega al suelo a los {d['t_primer_impacto']:.2f} s "
             f"con una rapidez de {d['v_primer_impacto']:.2f} m/s.")
    dif = ("prácticamente nula (menor que 0.0001 %)" if d["error_energia"] < 1e-4
           else f"de solo {d['error_energia']:.4f} %")
    c.append(f"Por conservación de la energía, v = √(v0² + 2gh) = {d['v_teorica']:.2f} m/s; la "
             f"diferencia con la simulación es {dif}, lo que valida el modelo.")
    c.append("Sin resistencia del aire, el tiempo de caída y la rapidez de impacto NO dependen "
             "de la masa: la masa solo escala las energías (pruebe duplicarla). La energía "
             "potencial se transforma en cinética, y su suma se mantiene constante en el aire.")
    if p["v0"] > 0:
        c.append(f"Al lanzar hacia arriba, el objeto sube {p['v0'] ** 2 / (2 * p['g']):.2f} m por "
                 f"encima del punto de partida; en el punto más alto toda su energía es "
                 f"potencial (altura máxima {d['altura_max']:.2f} m).")
    if p["rebotes"] > 0 and len(sim["tramos"]) > 1:
        if p["e"] >= 0.9999:
            c.append("Con e = 1 (choque perfectamente elástico) no se pierde energía: el objeto "
                     "vuelve siempre a la misma altura.")
        else:
            c.append(f"Con e = {p['e']:.2f}, en cada rebote se conserva e² = {p['e'] ** 2:.2f} de "
                     f"la energía y la altura de rebote cae al mismo factor. Tras "
                     f"{int(d['n_rebotes'])} rebote(s) se ha disipado {d['pct_disipada']:.1f} % de "
                     "la energía inicial (calor, sonido y deformación en el choque).")
    elif p["rebotes"] == 0:
        c.append("Se simuló solo la caída hasta el primer impacto (0 rebotes).")
    return c
