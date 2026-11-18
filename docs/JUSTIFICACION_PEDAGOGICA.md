# Justificación pedagógica e investigación

**Asignatura elegida:** Física (mecánica).
**Tema 1:** Tiro parabólico. **Tema 2:** Caída libre y conservación de la energía mecánica.

## 1. ¿Por qué estos dos temas están relacionados?

Ambos describen el movimiento de un cuerpo bajo la **gravedad como única fuerza relevante** (aceleración constante g hacia abajo). El tiro parabólico es la combinación de una caída libre en vertical con un movimiento uniforme en horizontal; por eso lo que se aprende en el Tema 2 (v = v0 − g·t, y = h0 + v0·t − ½gt²) se reutiliza directamente en el Tema 1. El puente conceptual entre ambos es la **energía mecánica**: en los dos se observa cómo la energía potencial y la cinética se intercambian y cuándo su suma se conserva (sin aire) o no (con aire o en un choque inelástico).

## 2. Fundamento teórico

**Tiro parabólico.** Con rapidez inicial v0 y ángulo θ: vx = v0·cosθ (constante) y vy = v0·sinθ − g·t. Posición: x = v0·cosθ·t ; y = h0 + v0·sinθ·t − ½·g·t². El tiempo de vuelo sale de y(t) = 0. Desde el suelo, el alcance es R = v0²·sin(2θ)/g, máximo a 45°, y ángulos complementarios dan el mismo alcance. Con h0 > 0, el ángulo óptimo es menor que 45°. Con resistencia del aire se añade F = −½·ρ·Cd·A·|v|·v (ρ = 1.225 kg/m³; Cd ≈ 0.47 para una esfera), que no tiene solución analítica sencilla y por eso se integra numéricamente (Runge-Kutta de 4.º orden, paso 1 ms).

**Caída libre y energía.** v = v0 − g·t ; y = h0 + v0·t − ½gt². La conservación de la energía (½mv² + mgy = constante) permite obtener la rapidez de impacto v = √(v0² + 2gh0) sin usar el tiempo: el simulador la calcula de las dos maneras y las compara. En un rebote, la rapidez se multiplica por el coeficiente de restitución e, de modo que la energía se multiplica por e² y la altura máxima de cada tramo también.

## 3. ¿Por qué un simulador y por qué así?

* **Experimentar antes de memorizar.** El estudiante cambia una variable a la vez y observa el efecto (aprendizaje por indagación).
* **Varias representaciones.** Cada resultado se muestra como número (indicadores), gráfica y texto (conclusiones), lo que ayuda a conectar fórmula, imagen e interpretación.
* **Contraste de modelos.** Con la opción de arrastre se ve la trayectoria real frente a la ideal y se cuantifica la diferencia: se entiende qué supone cada modelo.
* **Validación pedagógica.** Los datos imposibles (ángulo 95°, e = 2, masa 0) se rechazan con un mensaje que explica el porqué, en vez de dar resultados absurdos.
* **Escenarios.** Cuatro por tema, para guiar la exploración (Luna, Marte, acantilado, rebotes).

## 4. Objetivos de aprendizaje

1. Identificar que los movimientos horizontal y vertical son independientes en el tiro parabólico.
2. Relacionar ángulo, rapidez, altura y gravedad con alcance, altura máxima y tiempo de vuelo.
3. Explicar por qué la masa no influye en el tiempo de caída sin aire, pero sí en las energías.
4. Aplicar la conservación de la energía mecánica y reconocer cuándo deja de cumplirse.
5. Interpretar gráficas de posición, velocidad y energía.

## 5. Experimentos guiados (para la sustentación)

| # | Pregunta | Qué hacer | Qué se debería observar |
|---|---|---|---|
| 1 | ¿Qué ángulo da más alcance? | Tema 1, escenario 1; mirar la gráfica *Alcance vs. ángulo* | Máximo en 45°; 30° y 60° dan igual alcance |
| 2 | ¿Y si se lanza desde una altura? | Escenario 2 (acantilado, 40 m) | El ángulo óptimo baja de 45°; mayor rapidez de impacto |
| 3 | ¿Cuánto cambia el aire el resultado? | Escenario 3, comparar con la curva punteada | El alcance cae más de la mitad y la energía no se conserva |
| 4 | ¿Y en otro planeta? | Escenario 4 (Luna, g = 1.62) | Alcance ≈ 6 veces mayor que en la Tierra (63.7 m → 385.8 m) |
| 5 | ¿Depende la caída de la masa? | Tema 2, escenario 1; cambiar masa 1.5 → 50 kg | Mismo tiempo y velocidad; solo cambian las energías |
| 6 | ¿Cuánta energía se pierde al rebotar? | Escenario 3 (e = 0.7, 5 rebotes) | Cada rebote conserva e² = 49 %; tras 5 rebotes queda 2.8 % |
| 7 | ¿Qué pasa con un choque perfecto? | Poner e = 1 | La energía se mantiene y la altura se repite |

## 6. Referencias sugeridas

Para citar en el informe académico (el equipo debe verificar la edición que consulte):
* Sears, Zemansky, Young y Freedman. *Física universitaria* (capítulos de movimiento en dos dimensiones y de energía).
* Serway y Jewett. *Física para ciencias e ingeniería* (movimiento de proyectiles, conservación de la energía).
* Resnick, Halliday y Krane. *Física* (movimiento con aceleración constante).
* Para el método numérico: cualquier texto de métodos numéricos sobre Runge-Kutta de 4.º orden.
