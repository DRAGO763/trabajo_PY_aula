# Guion de sustentación (≈ 10–12 minutos)

> Sugerencia: reparta las partes entre los 4 o 5 integrantes y que **cada uno pueda explicar el código de su parte**. El profesor suele preguntar “¿qué hace esta línea?”.

| Min | Qué se muestra | Quién (sugerido) |
|---|---|---|
| 0–1 | Problema, objetivo y por qué Física con estos dos temas | Integrante 1 |
| 1–3 | Fundamento teórico y justificación pedagógica (`docs/JUSTIFICACION_PEDAGOGICA.md`) | Integrante 1 |
| 3–4 | Arquitectura: Java → JSON → Python → gráficas → PDF (diagrama del README) | Integrante 2 |
| 4–6 | **Demo Java:** cambiar parámetros, mostrar validación con datos erróneos (ángulo 95, e = 2, campo vacío) | Integrante 2 |
| 6–7 | Mostrar `entrada.json` y explicar cada campo | Integrante 3 |
| 7–9 | **Demo Python:** escenarios 3 (aire) y Tema 2 con rebotes; leer indicadores y gráficas | Integrante 4 |
| 9–10 | Abrir el PDF generado: parámetros, indicadores, gráficas, conclusiones | Integrante 4 |
| 10–11 | Pruebas: 21 de Python + 27 de Java; mostrar que pasan | Integrante 5 |
| 11–12 | Conclusiones, limitaciones y mejoras posibles | Integrante 5 |

## Preguntas probables y cómo responder

* **¿Por qué Java y Python y no todo en uno?** Es el requisito del proyecto; además cada lenguaje hace lo que mejor hace aquí: Java, interfaz y validación; Python, cálculo numérico, gráficas y PDF.
* **¿Cómo se comunican?** Java escribe `entrada.json`, lanza Python con `ProcessBuilder` pasando la ruta, y Python responde con una línea JSON en la salida estándar que Java lee.
* **¿Qué pasa si Python falla o no está instalado?** Java detecta el error, lo muestra en un cuadro de diálogo y en el registro; no se cae.
* **¿Dónde se valida?** En Java (rangos del catálogo `Tema`/`Parametro`, números finitos, enteros, reglas cruzadas). Python repite una validación defensiva por si el JSON se edita a mano.
* **¿Por qué RK4 y no Euler?** Es mucho más preciso con el mismo paso; sin aire coincide con la fórmula exacta (hay una prueba que lo comprueba).
* **¿Cómo sabe que los cálculos son correctos?** Se comparan con fórmulas conocidas (alcance v0²·sin2θ/g, altura máxima, tiempo de caída √(2h/g), e² por rebote) en `pruebas/test_fisica.py`.
* **¿Qué pasa con ángulo 90°?** Es válido: el proyectil sube y cae en vertical, alcance 0.
* **¿Qué mejoraría?** Viento, efecto Magnus, comparar dos ejecuciones en un mismo informe, exportar a CSV.
