"""Generacion de graficas (matplotlib, sin ventana) para cada tema."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

AZUL, NARANJA, VERDE, ROJO, GRIS = "#1f5fa8", "#e07b00", "#2e8b57", "#c0392b", "#7f8c8d"


def _guardar(fig, carpeta, nombre):
    ruta = os.path.join(carpeta, nombre)
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return ruta


def _estilo(ax, xl, yl, titulo):
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    ax.set_title(titulo, fontsize=11, fontweight="bold")
    ax.grid(alpha=0.3)


# ----------------------------------------------------------------- Tema 1
def graficas_tiro(carpeta, p, sim, ideal, barrido_main, barrido_ideal):
    res = []
    # 1) Trayectoria
    fig, ax = plt.subplots(figsize=(7.5, 4), constrained_layout=True)
    if p["usar_arrastre"]:
        ax.plot(ideal["x"], ideal["y"], "--", color=GRIS, label="Sin aire (ideal)")
    ax.plot(sim["x"], sim["y"], color=AZUL, lw=2,
            label="Con arrastre" if p["usar_arrastre"] else "Trayectoria")
    i = int(np.argmax(sim["y"]))
    ax.plot(sim["x"][i], sim["y"][i], "o", color=ROJO)
    ax.annotate(f"h máx = {sim['y'][i]:.1f} m", (sim["x"][i], sim["y"][i]),
                textcoords="offset points", xytext=(8, 6), fontsize=9)
    ax.plot(sim["x"][-1], 0, "s", color=VERDE)
    ax.annotate(f"alcance = {sim['x'][-1]:.1f} m", (sim["x"][-1], 0),
                textcoords="offset points", xytext=(-80, 12), fontsize=9)
    ax.set_ylim(bottom=min(0, -0.02 * max(sim["y"].max(), 1)))
    _estilo(ax, "x (m)", "y (m)", "Trayectoria del proyectil")
    ax.legend()
    res.append(("Trayectoria", _guardar(fig, carpeta, "grafica_1_trayectoria.png"),
                "Posición del proyectil en el plano vertical."))
    # 2) Velocidades
    fig, ax = plt.subplots(figsize=(7.5, 3.6), constrained_layout=True)
    ax.plot(sim["t"], sim["vx"], color=NARANJA, lw=2, label="vx (horizontal)")
    ax.plot(sim["t"], sim["vy"], color=AZUL, lw=2, label="vy (vertical)")
    ax.axhline(0, color="k", lw=0.8)
    _estilo(ax, "t (s)", "velocidad (m/s)", "Componentes de la velocidad en el tiempo")
    ax.legend()
    res.append(("Velocidades", _guardar(fig, carpeta, "grafica_2_velocidades.png"),
                "vx es constante sin aire; vy decrece linealmente por la gravedad."))
    # 3) Energias
    fig, ax = plt.subplots(figsize=(7.5, 3.6), constrained_layout=True)
    ax.plot(sim["t"], sim["ec"], color=NARANJA, lw=2, label="Cinética")
    ax.plot(sim["t"], sim["ep"], color=VERDE, lw=2, label="Potencial")
    ax.plot(sim["t"], sim["em"], color="k", lw=2, ls="--", label="Mecánica total")
    _estilo(ax, "t (s)", "energía (J)", "Energías durante el vuelo")
    ax.legend()
    res.append(("Energías", _guardar(fig, carpeta, "grafica_3_energias.png"),
                "Intercambio entre energía cinética y potencial; la total es constante solo sin aire."))
    # 4) Alcance vs angulo
    fig, ax = plt.subplots(figsize=(7.5, 3.8), constrained_layout=True)
    ang, alc, ao, am = barrido_main
    if p["usar_arrastre"]:
        ai, ali, aoi, ami = barrido_ideal
        ax.plot(ai, ali, "--", color=GRIS, label=f"Sin aire (óptimo {aoi:.0f}°)")
    ax.plot(ang, alc, color=AZUL, lw=2,
            label=("Con arrastre" if p["usar_arrastre"] else "Alcance") + f" (óptimo {ao:.0f}°)")
    ax.plot(ao, am, "o", color=ROJO)
    ax.axvline(p["angulo"], color=VERDE, ls=":", label=f"Ángulo usado ({p['angulo']:.0f}°)")
    _estilo(ax, "ángulo de lanzamiento (°)", "alcance (m)", "Alcance en función del ángulo")
    ax.legend(fontsize=8)
    res.append(("Alcance vs. ángulo", _guardar(fig, carpeta, "grafica_4_alcance_angulo.png"),
                "Barrido de 1° a 89° con la misma rapidez, altura y gravedad."))
    return res


# ----------------------------------------------------------------- Tema 2
def graficas_caida(carpeta, p, sim):
    res = []
    # 1) Posicion y velocidad
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.5, 5), sharex=True, constrained_layout=True)
    a1.plot(sim["t"], sim["y"], color=AZUL, lw=2)
    _estilo(a1, "", "altura (m)", "Altura en el tiempo")
    a2.plot(sim["t"], sim["v"], color=NARANJA, lw=2)
    a2.axhline(0, color="k", lw=0.8)
    _estilo(a2, "t (s)", "velocidad (m/s)", "Velocidad en el tiempo (positiva hacia arriba)")
    res.append(("Altura y velocidad", _guardar(fig, carpeta, "grafica_1_altura_velocidad.png"),
                "La pendiente de v(t) es -g; cada rebote invierte el sentido de la velocidad."))
    # 2) Energias
    fig, ax = plt.subplots(figsize=(7.5, 3.8), constrained_layout=True)
    ax.plot(sim["t"], sim["ec"], color=NARANJA, lw=2, label="Cinética")
    ax.plot(sim["t"], sim["ep"], color=VERDE, lw=2, label="Potencial")
    ax.plot(sim["t"], sim["em"], color="k", lw=2, ls="--", label="Mecánica total")
    _estilo(ax, "t (s)", "energía (J)", "Transformación y conservación de la energía")
    ax.legend()
    res.append(("Energías", _guardar(fig, carpeta, "grafica_2_energias.png"),
                "Ec + Ep = constante en el aire; en cada rebote con e < 1 la total disminuye."))
    # 3) Alturas de pico por tramo o energia vs altura
    tr = sim["tramos"]
    if len(tr) > 1:
        fig, ax = plt.subplots(figsize=(7.5, 3.6), constrained_layout=True)
        etiquetas = ["Inicial"] + [f"Reb. {k}" for k in range(1, len(tr))]
        ax.bar(etiquetas, [t_["h_pico"] for t_ in tr], color=AZUL)
        for i, t_ in enumerate(tr):
            ax.text(i, t_["h_pico"], f"{t_['h_pico']:.2f}", ha="center", va="bottom", fontsize=8)
        _estilo(ax, "tramo", "altura máxima (m)", "Altura máxima alcanzada en cada tramo")
        cap = f"Con e = {p['e']:.2f} la altura se reduce por el factor e² = {p['e'] ** 2:.2f} en cada rebote."
        nombre = "grafica_3_alturas_rebote.png"
        titulo = "Alturas de rebote"
    else:
        s = sim["t"] <= tr[0]["t_impacto"]
        fig, ax = plt.subplots(figsize=(7.5, 3.8), constrained_layout=True)
        ax.plot(sim["y"][s], sim["ec"][s], color=NARANJA, lw=2, label="Cinética")
        ax.plot(sim["y"][s], sim["ep"][s], color=VERDE, lw=2, label="Potencial")
        ax.plot(sim["y"][s], sim["em"][s], color="k", ls="--", lw=2, label="Mecánica total")
        _estilo(ax, "altura (m)", "energía (J)", "Energía en función de la altura")
        ax.legend()
        cap = "A mayor altura, más energía potencial; al bajar se convierte en cinética."
        nombre = "grafica_3_energia_altura.png"
        titulo = "Energía vs. altura"
    res.append((titulo, _guardar(fig, carpeta, nombre), cap))
    return res
