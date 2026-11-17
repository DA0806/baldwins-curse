# Etapa 5 · Campaña, jefe y epílogo

La partida se completa de principio a fin por la ruta prevista ([ruta.md](ruta.md)):

```text
plano de entrada → Atrio del Voto (3) → Cripta de las Ascuas (4) → Capilla del Último Sello (3) → epílogo
```

## Qué hay

- **Diez salas** con el contrato de la etapa 3 (`room_id`, `Spawns/<id>`, `RoomExit`, `unique_id`) y **cinco puntos de control**. Atrio 1 y 3 se rehicieron con el kit del Atrio; el Atrio 2 (sala de referencia) sólo cambia el objeto del pedestal: ahora es la Máscara del Voto, porque el Atrio enseña el Voto y la Cripta, el Ascua.
- **Tres zonas distintas** en geometría (huecos, cornisa, lápidas de cobertura, escalón alto), encuentros (custodios, acólitos, custodio sellado, jefe) y sonido (un ambiente por zona y música propia en la arena).
- **Enemigo a distancia** (`Scripts/Enemies/RangedEnemy.gd`, `EmberOrb.gd`) y **variante** del custodio (más salud y daño, anticipación más corta, armadura).
- **Jefe**, el Abad Sellado (`Scripts/Bosses/Boss.gd`, `FallingEmber.gd`): dos patrones, ventanas de vulnerabilidad marcadas por el sello del pecho, transición de fase y barra propia. El detalle está en el README principal.
- **Historia:**
  - Plano de entrada (`Scenes/Intro.tscn`).
  - Tres inscripciones: Cripta 1, Capilla 1 y Capilla 2.
  - Epílogo de victoria (`Scenes/Ending.tscn`), que vuelve al inicio con `GameSession.start_campaign()`. Es el punto de conexión del menú de la etapa 6.
- **Arte y sonido** de las zonas, los enemigos, el jefe, Baldwin (sustituye al caballero de procedencia pendiente), las armas y las ilustraciones. Los generó por código un agente en paralelo (`tools/gen_zone_assets.py`) con un contrato fijo de rutas, cuadros y pivotes. Procedencia en `docs/assets.md` y detalle en [assets_manifest.md](assets_manifest.md); hojas de revisión en `previews/`.

## Verificación

| Comprobación | Resultado |
| --- | --- |
| `tools/smoke.sh` y `--self-test` | OK |
| Etapas 1, 2, 3 y 4 | 62/0, 61/0, 64/0, 18/0 |
| Etapa 5 (`Tests/stage5_tests.gd`) | 45/0 |

La prueba de la etapa 5 cubre:
- **Ruta:** contrato (huecos ≤ 96 px y escalones ≤ 64 px, medidos sobre el salto real), recorrido completo de la intro al epílogo (llega con espada, maza, Voto y Ascua) y muerte con reaparición en cada uno de los cinco puntos.
- **Acólito:** 12 de daño, 9,6 con el Voto, se esquiva saltando y la lápida para la brasa.
- **Abad:** anticipaciones medidas (48 y 54 ticks), sin daño fuera de las ventanas, fase 2 (tiempos ×0,75, dos tajos por lluvia, cinco brasas a 64 px) y repetición tras morir.

Un jugador simulado vence al Abad con las cuatro combinaciones de arma y máscara. Sólo pulsa acciones del InputMap y lee lo mismo que vería una persona: la pose, las marcas de brasa y el sello. Los resultados (jugando sin fallos) fueron:

| Arma + máscara | Tiempo | Golpes recibidos |
| --- | --- | --- |
| Espada + Voto | 18 s | 0 |
| Espada + Ascua | 15 s | 0 |
| Maza + Voto | 19 s | 0 |
| Maza + Ascua | 17 s | 0 |

Capturas con el juego detenido en `capturas/` (once escenas, de la intro al epílogo); hojas en `hoja_capturas.png` y `hoja_capturas_grises.png`. Se reproducen con `"$GODOT" --path . -s res://tools/stage5_capture.gd`.

## Fallos encontrados y corregidos en el camino

- La brasa del acólito no dañaba: su máscara de colisión con los muros (capa 1) también tocaba el cuerpo del jugador y se borraba antes de aplicar el daño. Ahora sólo la apagan los cuerpos estáticos.
- Una sala que declaraba el pickup antes que al jugador retenía scripts al cerrar, por la referencia mutua entre `ItemPickup.gd` y `PlayerInventory.gd`. Las salas declaran primero al jugador y el HUD.
- La barra del jefe tapaba el texto de la máscara en el HUD: ahora va arriba en el centro.

## Duración

Cruzar las diez salas andando lleva poco más de un minuto, y un jugador perfecto vence al jefe en unos 15–20 s. Una primera partida real, con muertes, lectura de inscripciones y aprendizaje de los patrones, se estima en **8–15 minutos**, por debajo del objetivo de **20–35 minutos**. No se ha medido con personas. La forma de ajustarlo es observar partidas reales y después:
- subir la salud del Abad y de los custodios;
- añadir encuentros en las salas largas;
- alargar la Cripta y la Capilla con más tramos de plataformas, sin añadir salas nuevas a la ruta.

## Pendiente

- **Partidas con personas**: duración, dificultad del jefe (el jugador simulado no falla nunca) y lectura de las anticipaciones.
- **Grabación de una partida completa en tiempo real** (ruta y tiempo): la prueba recorre la ruta colocando al jugador en cada salida, no jugándola.
- **Arte**: el agente señala como más flojos los cuadros 3–5 de la muerte de Baldwin (caída rotada), su ciclo de andar algo rígido, los cuadros 2 y 8 del Abad y el fondo lejano de la Cripta (muy oscuro).
- **Audio**: sintetizado y validado por duración, pico y costura, pero no escuchado. Los bucles vienen normalizados al pico, así que bajé el bus Music a −9 dB; queda comprobarlo con altavoces.
- `Sprites/Characters/Knight_1/` y `Copper_Sword.png` ya no se usan: borrarlos o acreditarlos antes de distribuir.
- Las salas de la campaña salen de un generador temporal de esta sesión, que no está en el repositorio. Los `.tscn` son escenas normales y se editan en Godot a partir de ahora.
