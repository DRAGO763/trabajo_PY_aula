"""Tema 2 - Caida libre y conservacion de la energia mecanica (con rebotes).

Movimiento vertical con aceleracion constante -g (sin aire). En cada impacto con el
suelo la rapidez se multiplica por el coeficiente de restitucion e (0 a 1), por lo que
la energia mecanica se multiplica por e^2.
"""
import math
import numpy as np


def simular(p, dt=0.002):
    g, m, e = p["g"], p["masa"], p["e"]
    y0, v = p["h0"], p["v0"]            # v > 0: hacia arriba
    n_seg = int(p["rebotes"]) + 1
    t0 = 0.0
    T, Y, V = [], [], []
    tramos = []
    for k in range(n_seg):
        t_imp = (v + math.sqrt(v * v + 2 * g * y0)) / g
        if t_imp <= 1e-9:
            break
        n = max(int(t_imp / dt), 30)
        tt = np.linspace(0.0, t_imp, n)
        yy = y0 + v * tt - 0.5 * g * tt * tt
        yy[-1] = 0.0
        vv = v - g * tt
        T.append(t0 + tt)
        Y.append(yy)
        V.append(vv)
        h_pico = y0 + (v * v / (2 * g) if v > 0 else 0.0)
        tramos.append({"n": k, "t_inicio": t0, "t_impacto": t0 + t_imp,
                       "v_impacto": abs(float(vv[-1])), "h_pico": float(h_pico),
                       "ec_impacto": 0.5 * m * float(vv[-1]) ** 2})
        t0 += t_imp
        v = -e * float(vv[-1])
        y0 = 0.0
        if v < 1e-3:
            break
    if not tramos:
        raise ValueError("Con estos parametros no hay movimiento "
                         "(altura 0 y sin velocidad hacia arriba).")
    t, y, v = np.concatenate(T), np.concatenate(Y), np.concatenate(V)
    ec = 0.5 * m * v * v
    ep = m * g * y
    return {"t": t, "y": y, "v": v, "ec": ec, "ep": ep, "em": ec + ep, "tramos": tramos}
