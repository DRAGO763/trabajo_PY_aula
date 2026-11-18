# Simulador educativo de Física — Tiro parabólico y Caída libre / Energía

Proyecto de aula · Programación de Computadores (Prof. José Fabián Díaz Silva)
Integra **Java** (interfaz, captura, validación y JSON) con **Python** (cálculos, indicadores, gráficas y PDF).

**Equipo:** _(escribir aquí los nombres de los 4 o 5 integrantes)_

## 1. ¿Qué hace?

El usuario elige uno de los dos temas, modifica los parámetros (o carga un escenario) y pulsa **Validar y simular**:

```
Java (Swing)                    Python                              Resultado
captura + valida  ──JSON──▶  lee entrada.json                 ──▶  informe.pdf
parámetros                   calcula, indicadores, gráficas        gráficas PNG
muestra gráficas ◀────────── resultados.json                       resultados.json
```

| Tema | Qué se puede variar | Qué se obtiene |
|---|---|---|
| **1. Tiro parabólico** | rapidez, ángulo, altura inicial, gravedad, masa, resistencia del aire (Cd, área) | alcance, altura máxima, tiempo de vuelo, rapidez y ángulo de impacto, energías, ángulo óptimo, comparación con/sin aire |
| **2. Caída libre y energía** | altura, velocidad inicial, masa, gravedad, coeficiente de restitución e, nº de rebotes | tiempo y rapidez de impacto, verificación por conservación de energía, energía disipada por rebote, alturas de rebote |

Cada tema trae **4 escenarios** listos (por ejemplo: balón con resistencia del aire, el mismo tiro en la Luna, pelota con rebotes, caída en Marte). Cada ejecución crea una carpeta en `salidas/` con `entrada.json`, `resultados.json`, las gráficas y `informe.pdf`.

## 2. Requisitos

* **Java 11 o superior** (JDK, para compilar). Probado con JDK 21.
* **Python 3.9 o superior** con: `pip install -r requirements.txt` (numpy, matplotlib, reportlab).
* Java debe encontrar el comando `python3`, `python` o `py` en el PATH.

## 3. Compilar y ejecutar

Desde la carpeta del proyecto:

**Linux / macOS**
```bash
pip install -r requirements.txt
mkdir -p java/out && javac -encoding UTF-8 -d java/out java/src/simulador/*.java
java -cp java/out simulador.Main            # abre la interfaz gráfica
```

**Windows (PowerShell o CMD)**
```bat
pip install -r requirements.txt
mkdir java\out
javac -encoding UTF-8 -d java\out java\src\simulador\*.java
java -cp java\out simulador.Main
```

**Modo consola** (útil para pruebas, sin ventana):
```bash
java -cp java/out simulador.Main --cli tiro 3                 # escenario 3 del tema 1
java -cp java/out simulador.Main --cli caida h0=30 e=0.5 rebotes=4
```
Si la consola muestra caracteres raros, agregue `-Dfile.encoding=UTF-8` (en Windows, `chcp 65001`).

## 4. Pruebas

```bash
python3 -m unittest discover -s pruebas -v              # 21 pruebas de física, JSON y PDF
java -cp java/out simulador.PruebasValidador            # 27 pruebas del validador y del JSON
```
Resultados y casos de prueba: `docs/PRUEBAS.md`.

## 5. Estructura

```
java/src/simulador/   Main, VentanaPrincipal (Swing), Tema/Parametro (catálogo y rangos),
                      Validador, JsonUtil, Escenario, EjecutorPython, PruebasValidador
python/               simulador.py (entrada), fisica_tiro.py, fisica_caida.py,
                      analisis.py (indicadores y conclusiones), graficas.py, informe_pdf.py
escenarios/           los 8 escenarios en JSON (mismos valores que Escenario.java)
pruebas/              pruebas automáticas de Python
docs/                 justificación pedagógica, pruebas, guion de sustentación
ejemplos_salida/      un PDF generado por cada escenario
```

## 6. Formato del JSON de entrada (Java → Python)

```json
{
  "version": 1,
  "tema": "tiro_parabolico",
  "escenario": "Balón con resistencia del aire",
  "meta": { "origen": "Java", "fecha": "2026-11-17 22:53:32", "equipo": "..." },
  "parametros": { "v0": 30.0, "angulo": 40.0, "h0": 1.0, "g": 9.81, "masa": 0.45,
                  "usar_arrastre": true, "cd": 0.47, "area": 0.038 }
}
```
Python responde con una línea JSON `{"estado": "ok", "pdf": "...", "graficas": [...]}` o `{"estado": "error", "mensaje": "..."}`.

## 7. Limitaciones conocidas

* Modelo en 2D sin viento, rotación (efecto Magnus) ni variación de la densidad del aire con la altura.
* La caída con rebotes no incluye resistencia del aire (se puede ver en el Tema 1).
* Las ventanas y el PDF se probaron en Linux; en Windows/macOS siga los pasos de la sección 3 y verifique.
* Los escenarios existen en `Escenario.java` y en `escenarios/*.json`; si cambia uno, actualice el otro.

## 8. Créditos

La idea de “modificar un dato y ver qué pasa” y de validar los campos al instante se inspiró en el repositorio `Navix140/cuaderno-academico` (calculadora de notas en React, licencia MIT). **No se reutilizó código de ese repositorio**; este proyecto está hecho desde cero en Java y Python.
