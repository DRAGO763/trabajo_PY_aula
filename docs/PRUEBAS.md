# Plan y resultados de pruebas

Entorno de las pruebas: Linux, JDK 21 (compilado también con `--release 11`), Python 3.12, numpy 2.x, matplotlib 3.11, reportlab 5.
Fecha de ejecución: 17 de noviembre de 2026. Todas las pruebas de esta página se ejecutaron y pasaron.

## 1. Pruebas automáticas de Python (21) — `python3 -m unittest discover -s pruebas -v`

| Grupo | Prueba | Qué comprueba |
|---|---|---|
| Tiro | alcance con fórmula clásica | R = v0²·sin(2θ)/g (20 m/s, 45°) |
| Tiro | altura máxima y tiempo | (v0·sinθ)²/2g y 2·v0·sinθ/g |
| Tiro | ángulos complementarios | 30° y 60° dan el mismo alcance |
| Tiro | energía sin aire | Em constante (variación < 1e-6 relativa) |
| Tiro | arrastre | reduce alcance y energía |
| Tiro | arrastre → 0 | el modelo numérico coincide con el ideal (±0.01 m) |
| Tiro | Luna | alcance > 5 veces el de la Tierra |
| Tiro | sin movimiento | lanza error controlado |
| Tiro | ángulo óptimo | 45° desde el suelo |
| Caída | rapidez de impacto | √(2gh) |
| Caída | tiempo de caída | √(2h/g) |
| Caída | energía en vuelo | Em constante (< 1e-9 relativa) |
| Caída | masa | no cambia el tiempo (1 kg vs 50 kg) |
| Caída | rebotes | energía final = e^(2n); altura de rebote = e²·h |
| Caída | choque elástico | e = 1 conserva la energía |
| Caída | lanzamiento hacia arriba | altura máxima h0 + v0²/2g |
| Caída | sin movimiento | lanza error controlado |
| Integración | JSON → PDF (tiro y caída) | Python lee el JSON, genera un archivo que empieza con `%PDF-` y pesa más de 5 KB |
| Integración | datos inválidos / tema desconocido | respuesta `{"estado":"error"}` y código de salida 2 |

Resultado: `Ran 21 tests ... OK`.

## 2. Pruebas del validador y del JSON en Java (27) — `java -cp java/out simulador.PruebasValidador`

Cubren: valores por defecto válidos; coma decimal (9,81); texto no numérico; campo vacío; NaN; Infinity; velocidad negativa; ángulo 91° (rechazado) y 90° (aceptado); gravedad 0; masa 0; altura 0 con ángulo 0; arrastre activo con Cd = 0; arrastre inactivo ignora Cd vacío; e = 1.5 (rechazado) y e = 1 (aceptado); rebotes decimales o > 20; caída con h = 0 y v = 0 (rechazada) y con v = 10 (aceptada); escritura correcta del JSON (tema, comillas escapadas, booleanos, números con punto); lectura de rutas con barras invertidas y de listas.

Resultado: `27 correctas, 0 fallidas`.

## 3. Pruebas de integración Java → JSON → Python → PDF (modo consola)

Se ejecutaron los 8 escenarios con `java -cp java/out simulador.Main --cli <tema> <n>`. Cada uno creó `entrada.json`, `resultados.json`, las gráficas y `informe.pdf`.

| Escenario | Resultado clave | Verificación manual |
|---|---|---|
| Tiro 1 · ideal a 45° | alcance 63.71 m, h máx 15.93 m, 3.60 s | 25²/9.81 = 63.71 ✔ |
| Tiro 2 · acantilado 40 m | alcance 68.35 m, óptimo 30° | ángulo óptimo < 45° ✔ |
| Tiro 3 · balón con aire | alcance 38.91 m (−57.5 % vs. ideal), óptimo 38° | menor que el ideal ✔ |
| Tiro 4 · Luna (g = 1.62) | alcance 385.80 m | 25²/1.62 = 385.80 ✔ |
| Caída 1 · 20 m | 2.02 s, 19.81 m/s | √(2·20/9.81) = 2.02 s ✔ |
| Caída 2 · hacia arriba 12 m/s | h máx 12.34 m, 2.81 s | 5 + 12²/(2·9.81) = 12.34 ✔ |
| Caída 3 · 5 rebotes, e = 0.7 | 97.18 % de energía disipada | 1 − 0.7¹⁰ = 0.9718 ✔ |
| Caída 4 · Marte | 3.28 s | √(2·20/3.71) = 3.28 s ✔ |

Los PDF de estos escenarios están en `ejemplos_salida/`.

## 4. Pruebas de datos inválidos (consola)

| Entrada | Respuesta |
|---|---|
| `tiro angulo=95` | “Ángulo de lanzamiento: debe estar entre 0 y 90 °.” (código 3, no se ejecuta Python) |
| `tiro v0=abc` | “Rapidez inicial: 'abc' no es un número válido.” |
| `caida e=2` | “Coeficiente de restitución e: debe estar entre 0 y 1.” |
| `caida h0=0 v0=0` | “…no hay movimiento: suba la altura o dé una velocidad positiva.” |
| `tiro usar_arrastre=true cd=0` | “Con resistencia del aire, Cd y el área deben ser mayores que 0.” |
| JSON editado a mano con un parámetro faltante | Python devuelve `{"estado":"error","mensaje":"Falta el parámetro 'g'..."}` (código 2) |

## 5. Prueba de la interfaz gráfica

La ventana se ejecutó en un entorno gráfico virtual (Xvfb): se pulsó “Validar y simular” con el escenario 1 del Tema 1; se generó el PDF, se habilitó el botón “Abrir PDF” y la gráfica apareció en el panel derecho (`docs/captura_interfaz.png`).
**Pendiente para el equipo:** probar la ventana en sus propios computadores (Windows) y marcar en la lista:

- [ ] Se abre la ventana y cambian los campos al elegir otro tema
- [ ] Los campos con error se pintan de rojo y aparece el mensaje
- [ ] “Abrir PDF” y “Abrir carpeta” funcionan
- [ ] El comando `python`/`py` es encontrado por Java

## 6. Casos no cubiertos

No se usó JUnit (se evita dependencia externa); las pruebas de Java son un programa propio. No se probaron pantallas de alta resolución ni macOS.
