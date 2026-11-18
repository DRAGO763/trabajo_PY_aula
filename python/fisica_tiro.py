"""Tema 1 - Tiro parabolico.

Dos modelos:
  * ideal: sin resistencia del aire (solucion analitica).
  * con arrastre: resistencia cuadratica F = -k |v| v, con k = 1/2 * rho * Cd * A,
    integrada numericamente con Runge-Kutta de 4.o orden (RK4).
"""
import math
import numpy as np

RHO_AIRE = 1.225  # kg/m^3 (aire a nivel del mar)


def _componentes(p):
    a = math.radians(p["angulo"])
    return p["v0"] * math.cos(a), p["v0"] * math.sin(a)


def _empaquetar(p, t, x, y, vx, vy):
    m, g = p["masa"], p["g"]
    v2 = vx * vx + vy * vy
    ec = 0.5 * m * v2
    ep = m * g * y
    return {"t": t, "x": x, "y": y, "vx": vx, "vy": vy,
            "ec": ec, "ep": ep, "em": ec + ep}


def simular_ideal(p, puntos=400):
    g, h0 = p["g"], p["h0"]
    vx, vy = _componentes(p)
    t_vuelo = (vy + math.sqrt(vy * vy + 2 * g * h0)) / g
    if t_vuelo <= 1e-9:
        raise ValueError("Con estos parametros el proyectil no se mueve "
                         "(tiempo de vuelo nulo).")
    t = np.linspace(0.0, t_vuelo, puntos)
    x = vx * t
    y = h0 + vy * t - 0.5 * g * t * t
    y[-1] = 0.0
    return _empaquetar(p, t, x, y, np.full_like(t, vx), vy - g * t)


def simular_arrastre(p, dt=0.001, max_pasos=3_000_000, max_puntos=1500):
    # El modelo ideal valida que realmente haya vuelo.
    simular_ideal(p, puntos=10)
    g, m = p["g"], p["masa"]
    kk = 0.5 * RHO_AIRE * p["cd"] * p["area"] / m
    vx0, vy0 = _componentes(p)

    def deriv(s):
        _, _, vx, vy = s
        v = math.hypot(vx, vy)
        return (vx, vy, -kk * v * vx, -g - kk * v * vy)

    s = (0.0, p["h0"], vx0, vy0)
    hist = [(0.0,) + s]
    t = 0.0
    for _ in range(max_pasos):
        k1 = deriv(s)
        k2 = deriv(tuple(s[i] + 0.5 * dt * k1[i] for i in range(4)))
        k3 = deriv(tuple(s[i] + 0.5 * dt * k2[i] for i in range(4)))
        k4 = deriv(tuple(s[i] + dt * k3[i] for i in range(4)))
        nuevo = tuple(s[i] + dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
                      for i in range(4))
        if nuevo[1] < 0.0:  # cruzo el suelo: interpolar linealmente
            f = s[1] / (s[1] - nuevo[1]) if s[1] != nuevo[1] else 0.0
            nuevo = tuple(s[i] + f * (nuevo[i] - s[i]) for i in range(4))
            nuevo = (nuevo[0], 0.0, nuevo[2], nuevo[3])
            hist.append((t + f * dt,) + nuevo)
            break
        t += dt
        s = nuevo
        hist.append((t,) + s)
    else:
        raise RuntimeError("La simulacion no termino (revise los parametros).")

    arr = np.array(hist)
    if len(arr) > max_puntos:
        idx = np.unique(np.append(np.linspace(0, len(arr) - 1, max_puntos).astype(int),
                                  len(arr) - 1))
        arr = arr[idx]
    return _empaquetar(p, arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3], arr[:, 4])


def barrido_angulos(p, con_arrastre, paso=1.0):
    """Alcance en funcion del angulo de lanzamiento (1 a 89 grados)."""
    angulos = np.arange(1.0, 90.0, paso)
    alcances = []
    for a in angulos:
        q = dict(p, angulo=float(a))
        sim = simular_arrastre(q, dt=0.004) if con_arrastre else simular_ideal(q, puntos=50)
        alcances.append(float(sim["x"][-1]))
    alcances = np.array(alcances)
    i = int(np.argmax(alcances))
    return angulos, alcances, float(angulos[i]), float(alcances[i])
