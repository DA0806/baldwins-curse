# Checkpoint 3 · Kingdom Baldwin en Python

Ejecuta `python3 main.py` desde la raíz con Python 3.10 o posterior. El primer menú es el del juego de consola. Pruebas con `python3 -m unittest discover -s tests_cp3 -v`.

La expedición de Godot es el proyecto gráfico. Esta versión académica continúa el prototipo de consola de los checkpoints anteriores.


El [README principal](../README.md#checkpoint-3--juego-de-consola) contiene los diagramas del grafo y del árbol de misiones.

## Estructuras en juego

| Estructura | Decisión y uso | Complejidad |
| --- | --- | --- |
| Lista de adyacencia | Es una representación reutilizable para un mapa de pocas puertas por sala. BFS usa cola para encontrar una ruta con el menor número de cruces; DFS recorre las salas alcanzables con las puertas disponibles. | Espacio O(V + E). BFS y DFS O(V + E). |
| Árbol con índice por ID | Expresa el prerrequisito único de cada objetivo. El diario usa preorden para dibujar jerarquía y un recorrido por niveles para sugerir objetivos disponibles. | Recorridos O(n). Preorden usa O(h) de pila auxiliar; el recorrido por niveles usa una cola. |
| Diccionario por ID de sala | Guarda el estado del mundo sin buscar toda una lista al entrar. Las consultas toleran claves ausentes. El panel permite consultar, actualizar, insertar o eliminar entradas permitidas y mostrar dos vistas del estado. | Consulta, inserción y eliminación O(1) esperado en la tabla. Las consultas que filtran o resumen todas las salas cuestan O(V). |
| Pila de historial | La última acción aplicada es la primera en revertirse. Cada entrada captura el estado previo de los sistemas que la acción puede alterar. | Apilar y desapilar O(1) amortizado; capturar o restaurar el estado añade el coste de copiar el estado mutable, O(S). |
| Colas de eventos y turnos | El movimiento consume el primer evento y rota al participante activo. El orden queda definido de antemano y se conserva al deshacer. | Insertar o retirar en los extremos de un deque cuesta O(1); también rotar un turno. |
| Recursión | Cada rama de la mazmorra original se construye con el mismo procedimiento y termina al llegar a la profundidad máxima. | O(V) para el árbol original, con O(h) llamadas anidadas. |

El mapa determina dónde se puede actuar. Completar el objetivo cambia el estado de la misión y puede modificar los caminos disponibles. Los recorridos reutilizan ese mismo estado de puertas y del mundo. La sala y su botín se consultan por ID.

Al deshacer se restaura la posición, la salud y podredumbre, la bolsa, los estados del mundo y las misiones, junto con la cola de eventos y los turnos anteriores. Un evento disparado al moverse vuelve a ocupar la primera posición que tenía antes del movimiento. La resurrección limpia el historial e impide deshacer la muerte.

## Cómo probarlo

- `1` permite moverse desde el Nexo a `atrio_1`, donde se completa El Despertar del Rey. `2` toma el tesoro de la sala y `3` deshace la última acción.
- `9` abre el mapa con alcance BFS, exploración DFS y ruta mínima. Desde el Nexo, la ruta a `capilla_3` no existe mientras siga sellada.
- `10` abre el diario, los objetivos disponibles por nivel y la ruta a una misión. `12` ejecuta el objetivo disponible en la sala.
- `11` consulta una sala, cambia su peligro, conecta o elimina salas auxiliares y muestra los filtros de tesoro y peligro. La sala actual y las salas de campaña están protegidas contra eliminación.
- `0` vuelve al menú anterior o sale desde el menú principal.

Las 15 pruebas pasaron en un directorio vacío al que se copiaron únicamente el lanzador, el paquete Python y las pruebas. Cubren las diez misiones, el sello de la Capilla, cambios de sala que alteran el grafo, deshacer y entradas inválidas en todos los menús. [Salida de pruebas](evidence-cp3/tests.txt) · [Sesión real desde main.py](evidence-cp3/session.txt).

## Procedencia del CP2 y participación

Según el README del prototipo CP2 que entregó el equipo:

| Integrante | Aporte documentado en el prototipo |
| --- | --- |
| Diego Arau | Generación recursiva, marcado de tesoros y mediciones por nivel. |
| Felipe Cañas | Pila de historial y operaciones para deshacer. |
| José Luis Gutiérrez | Cola FIFO de eventos, reversión de efectos y cola rotativa de turnos. |
| Matthew Huezo | Integración de los módulos, menús y casos límite. |

Esta tabla describe la procedencia del código previo. La participación del CP3 se evalúa por contribuciones propias verificables en GitHub. Cada integrante debe confirmar y subir sus aportes reales con sus propias credenciales.

Fuentes: [consigna de Canvas](https://keyinstitute.instructure.com/courses/301/assignments/3018) y [presentación del equipo](https://www.canva.com/design/DAHakVJnpz8/joLy-_jfAcLhmNPEA9EajQ/edit).
