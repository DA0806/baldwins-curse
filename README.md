# Baldwin's Curse

Aventura de plataformas y acción 2D en Godot 4.7 con GDScript. Estado actual: **prototipo, etapas 0 a 6 del roadmap**: campaña completa de diez salas en tres zonas, del título al epílogo, con jefe final, menús navegables con teclado, pausa, guardado en el último brasero y ajustes de sonido, pantalla y efectos. Arte y sonido propios generados por código (`tools/gen_atrio_assets.py` y `tools/gen_zone_assets.py`). Falta la build 1.0 (etapa 7).

- Alcance propuesto de la 1.0: [docs/alcance-1.0.md](docs/alcance-1.0.md)
- Inventario de assets y procedencias: [docs/assets.md](docs/assets.md)
- Guía de arte: [docs/arte.md](docs/arte.md) · entrega de la sala de referencia: [docs/etapa4/](docs/etapa4/README.md)

## Arranque desde cero

1. Instala **Godot 4.7.2 Standard** (la versión con la que se probó; el proyecto declara la serie 4.7 y no usa C#): <https://godotengine.org/download/archive/4.7.2-stable/>
2. Clona el repositorio.

   ```bash
   git clone https://github.com/DA0806/baldwins-curse.git
   ```

3. En Godot usa **Importar**, elige `project.godot` y pulsa `F5`. Arranca la pantalla de título (`Scenes/UI/Title.tscn`). El laboratorio de movimiento y combate sigue en `Scenes/world.tscn` (ábrelo y pulsa `F6`).

El juego no necesita el servidor de Godot AI para arrancar (ver más abajo).

## Controles actuales

| Tecla | Acción |
| --- | --- |
| `←` / `→` | Caminar |
| `Espacio` / `↑` | Saltar (altura variable según cuánto se mantenga) |
| `R` | Recoger o intercambiar el objeto más cercano |
| `Z` / `X` | Ataque con el arma de la ranura 1 / 2 (una ranura vacía no hace nada) |
| `C` / `V` | Máscara anterior / siguiente |
| `Esc` / `P` | Pausa |
| `F3` | Mostrar u ocultar zonas de golpe y vulnerables (sólo en builds de depuración) |

Las teclas viven en el mapa de entradas de `project.godot`; los avisos en pantalla y el HUD las leen de ahí.

**Recogida.** Una pulsación de `R` actúa sobre un solo pickup: el elegible más cercano y, si hay empate, el primero en el árbol de escena. Un arma nueva entra en el primer hueco libre. Con las dos ranuras ocupadas reemplaza la **ranura de intercambio** (la del último ataque válido, o la 1 al empezar; el HUD la marca con el borde encendido y la tecla entre corchetes) y el arma desplazada queda en el suelo con su aviso.

## Menús, guardado y ajustes (etapa 6)

Informe de la etapa: [docs/etapa6/README.md](docs/etapa6/README.md).

**Menús.** Todo se maneja con teclado: flechas para moverse, `Intro` o `Espacio` para aceptar y `Esc` para volver. El foco se marca con un borde de brasa.
- **Título:** Continuar, Nueva partida, Ajustes, Controles, Créditos y Salir.
- **Pausa** (`Esc`/`P`, sólo dentro de una sala): Reanudar, Volver al último brasero, Ajustes, Controles y Volver al título.
- El foco empieza en Continuar si hay partida y, si no, en Nueva partida.
- Con la pausa abierta el mundo no recibe entradas, y al reanudar se esperan dos cuadros para que la tecla de confirmar (Espacio también salta) no llegue al jugador.

**Guardado.** Una ranura en `user://savegame.json` (JSON versionado, `SaveGame.VERSION = 1`) con la última activación de un brasero:
- **Qué guarda:** sala, punto, salud de reaparición, armas, máscaras y recogidas únicas, todo por ID, más tiempo, reintentos y si la partida está completada.
- **Cuándo:** al empezar una partida, al encender cada brasero y al ganar. Sólo se guardan las partidas empezadas desde el título; abrir una sala suelta (F6, el smoke) no toca la partida.
- **Escritura segura:** se escribe un temporal, la versión anterior pasa a `.bak` y el temporal ocupa su sitio. Si el principal falta o está dañado, se usa la copia.
- **Estados del archivo:** el título dice siempre en qué estado está (no hay, dañado, otra versión, sala inexistente, completada) y sigue funcionando. Los objetos con un ID que ya no existe se omiten con aviso.
- **Nueva partida con guardado:** pide confirmación, con «No» enfocado, porque sustituye la ranura.

**Ajustes.** Se guardan en `user://settings.cfg`, aparte del progreso, y sobreviven a reiniciar:
- Volumen general, de música y ambiente, y de efectos.
- Pantalla completa.
- Efectos reducidos: destellos de daño más suaves y marcas de brasa del jefe sin parpadeo. Los avisos de peligro se siguen leyendo por la forma.

La pantalla **Controles** lista las teclas reales del InputMap, con sus nombres en español.

## Combate

Cada ataque tiene anticipación, ventana activa y recuperación, definidas en el arma (`WeaponData`). Los datos del golpe se fijan al aceptarlo: arma, orientación y daño. Sólo daña durante la ventana activa, hacia donde mira el personaje, y a cada objetivo una vez como máximo. Mantener la tecla no repite el ataque y pulsar antes de que acabe el enfriamiento no hace nada.

| Arma | ID | Daño | Alcance | Anticipación | Ventana | Recuperación | Enfriamiento |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Copper Sword | `copper_sword` | 20 | 60 px | 0,16 s | 0,08 s | 0,16 s | 0,4 s |
| Maza de prueba | `test_mace` | 35 | 44 px | 0,28 s | 0,10 s | 0,32 s | 0,8 s |

El jugador tiene 100 de salud (barra arriba a la izquierda) y 0,6 s de invulnerabilidad tras cada impacto. Recibir daño interrumpe su ataque y lo empuja. Al morir, la sala reintenta sola después de 1 s: el jugador vuelve al punto de aparición con la salud completa y sus armas, y el enemigo y el maniquí vuelven a su estado inicial.

El enemigo terrestre (60 de salud, 15 de daño) patrulla alrededor de su origen, persigue al jugador si lo detecta y anticipa cada golpe durante 0,5 s: cambia de color, muestra `!` y levanta la hoja antes de extenderla.

Las zonas de golpe (rojo) y las vulnerables (verde) se muestran con `F3` en builds de depuración. Las capas de física tienen nombre en `project.godot` (`player_hitbox`, `enemy_hurtbox`, etc.).

## Máscaras

| Máscara | ID | Efecto | Icono |
| --- | --- | --- | --- |
| Máscara del Voto | `mask_vow` | ×0,80 al daño recibido (20 → 16) | óvalo marfil |
| Máscara de Ascua | `mask_ember` | ×1,25 al daño de arma (20 → 25) | triángulo de cobre |

Los valores viven en `Items/Masks/*.tres` (`passive_stat_multiplier`). Sólo cuenta la máscara activa y cada efecto se aplica en un único sitio: el defensivo en `Health.take_damage` (vía `PlayerInventory.modify_incoming_damage`) y el ofensivo al aceptar el ataque (`Player.execute_attack`), así que cambiar de máscara a mitad de un golpe no altera su daño.

`C`/`V` recorren el cinto en círculo. Tras un cambio efectivo hay 1 s de recarga, durante la cual se ignoran las pulsaciones. Con una sola máscara o ninguna no hay cambio y no se gasta la recarga. El cinto admite 3; con el cinto lleno, una máscara nueva sustituye a la activa y la anterior queda en el suelo. El HUD muestra icono, nombre, efecto y una barra de recarga (el icono se apaga mientras dura).

## Campaña (etapa 5)

Diez salas en tres zonas, del plano de entrada al epílogo. Diagrama y contrato de salas en [docs/etapa5/ruta.md](docs/etapa5/ruta.md); informe de la etapa en [docs/etapa5/README.md](docs/etapa5/README.md).

| Zona | Salas | Enseña | Encuentros |
| --- | --- | --- | --- |
| Atrio del Voto | `atrio_1`–`atrio_3` | Salto, espada, primer enemigo, Máscara del Voto | Maniquí, custodio, dos guardianes |
| Cripta de las Ascuas | `cripta_1`–`cripta_4` | Máscara de Ascua, Maza de la Cripta, enemigo a distancia | Custodio, acólito, custodio con dos acólitos |
| Capilla del Último Sello | `capilla_1`–`capilla_3` | Custodio sellado (variante), antesala con punto de control | El Abad Sellado |

Hay cinco puntos de control (braseros) y tres inscripciones que cuentan la motivación de Baldwin; el texto aparece al acercarse.

**Acólito de la Ascua.** Anticipa cada lanzamiento durante 0,6 s alzando el incensario y lanza una brasa en línea recta (12 de daño). Se puede saltar o esquivar cubriéndose tras una lápida.

**El Abad Sellado** (300 de salud). Tiene dos patrones con forma, ritmo y sonido distintos:
- **Tajo bajo:** echa la guadaña atrás durante 0,8 s con un chirrido y barre 104 px a ras de suelo. Se salta.
- **Lluvia de ascuas:** alza el incensario durante 0,9 s con un tañido y marca en el suelo dónde caen tres brasas, separadas 80 px. Los huecos entre marcas son seguros.

Después de cada patrón queda vulnerable (guadaña clavada 1,3 s o agotado 1,6 s) y el sello del pecho brilla. Fuera de esas ventanas no recibe daño. A la mitad de salud ruge y pasa a la fase 2: anticipaciones un 25 % más cortas, dos tajos por cada lluvia y lluvias de cinco brasas a 64 px. Usa el mismo contrato de salud y daño que los demás enemigos, así que el Voto y el Ascua le afectan igual.

**Punto de control.** Tocar el brasero lo enciende (crece y cambia a brasa) y guarda la sala, el punto, salud completa de reaparición, armas, máscaras y recogidas únicas. Cada nueva entrada vuelve a guardar: cuenta la última activación. La partida empieza con un punto implícito en la entrada del Atrio 1.

**Morir o caer** recarga la sala del último punto con ese estado: enemigos y objetos transitorios vuelven a su sitio, los objetos recogidos antes del punto no reaparecen y los recogidos después sí (y salen del inventario). El epílogo muestra tiempo y reintentos, y `R` vuelve al plano de entrada.

**Contrato de estado.** `GameSession` (autoload, `Scripts/GameSession.gd`) guarda el estado en memoria como un diccionario de datos simples: `room_id`, `spawn_id`, salud, inventario por IDs de `ItemCatalog` y la lista de `unique_id` recogidos. No guarda nodos ni rutas de escena: las salas se resuelven con `GameSession.ROOMS` y los objetos con `ItemCatalog`. El guardado de la etapa 6 usará este formato.

## Sala de referencia (etapa 4)

El Atrio 2 tiene el arte, el sonido y la transición de referencia: tiles de 16 px alineados con la colisión, fondo en dos planos, brasero como punto de control, custodio con una pose por fase de ataque, máscara sobre pedestal, foso con púas y arco de salida con estandartes. El ambiente entra y sale con fundido y cada cambio de sala funde a negro. Reglas en [docs/arte.md](docs/arte.md); capturas a tres resoluciones, en grises y la grabación en [docs/etapa4/](docs/etapa4/README.md).

El arte y el audio propios se regeneran con `python3 tools/gen_atrio_assets.py` (Pillow y numpy).

## Escena de prueba

`Scenes/world.tscn` es el laboratorio de movimiento y combate: una sala de 1920×360 con la cámara limitada a ella. No forma parte de la partida (no tiene `room_id`): caer devuelve al `SpawnPoint` y morir reinicia el encuentro sin recargar.

| Elemento | Posición | Para probar |
| --- | --- | --- |
| Maniquí | x 90 | Golpes: muestra cuántos recibió y el daño del último |
| Espada y maza | x 186 y 468 | Recogida e intercambio |
| Hueco | x 560–656 (96 px) | Salto largo, gracia al dejar el borde, caída y reaparición |
| Techo corto | x 800–928, 32 px sobre la cabeza | Golpe contra techo y corrección de esquinas |
| Escalones | 32 px (x 1000) y 64 px (x 1064) | Altura de salto corto y largo |
| Enemigo terrestre | origen en x 1560, zona de ±140 px | Duelo, daño recibido, muerte y reintento |
| Paredes | x 0 y x 1920 | Límites de sala y de cámara |

Caer por el hueco devuelve al jugador al punto de reaparición (`SpawnPoint`).

Medidas con los parámetros actuales, a 60 ticks por segundo:

| Medida | Valor |
| --- | --- |
| Salto largo (tecla mantenida) | 76,9 px de altura, 0,67 s en el aire |
| Salto corto (un tick) | 19,2 px de altura |
| Alcance horizontal a velocidad máxima | 129 px, igual a izquierda y derecha |
| Coyote time | salta hasta 7 ticks (0,117 s) después de dejar el borde |
| Buffer de salto | acepta la pulsación hasta 8 ticks (0,133 s) antes de aterrizar |
| Corrección de esquinas | desvía 6 px si sólo un rayo toca el techo |

Para repetirlas a mano: el salto largo sube al escalón de 64 y el corto no llega al de 32; corriendo desde la izquierda se cruza el hueco de 96 px; saltando con el borde del techo sobre la cabeza el personaje se desliza hacia fuera en lugar de frenarse.

## Verificación

Define la ruta del ejecutable una vez. En macOS está dentro de `Godot.app/Contents/MacOS/Godot`.

```bash
export GODOT=/ruta/a/Godot
```

**Smoke.** Importa el proyecto y arranca 120 iteraciones en headless la escena principal (el título) y la primera sala de la campaña. Falla si Godot devuelve un código distinto de 0 o si la salida contiene errores de parseo, carga o ejecución (Godot puede terminar con código 0 aunque un script no compile).

```bash
tools/smoke.sh
```

La autoprueba copia el proyecto, rompe un script a propósito y comprueba que el smoke lo detecta.

```bash
tools/smoke.sh --self-test
```

**Pruebas de la etapa 1.** Simulan entradas en la sala de pruebas y comprueban salto, coyote, buffer, techo, diez caídas con reaparición, cámara, recogida, intercambio, pickups solapados, invariante de dos ranuras y reenlace del HUD. Terminan con código 1 si algo falla.

```bash
"$GODOT" --headless --fixed-fps 60 --path . -s res://Tests/stage1_tests.gd
```

**Pruebas de la etapa 2.** Comprueban ranura vacía, daño exacto por arma, tiempos de la ventana activa, alcance en ambas direcciones, objetivo a la espalda, golpes duplicados, tecla mantenida y repetida, interrupción, muerte, reintento y el enemigo (patrulla, anticipación, derrota y victoria).

```bash
"$GODOT" --headless --fixed-fps 60 --path . -s res://Tests/stage2_tests.gd
```

**Pruebas de la etapa 3.** Comprueban 20 → 16 con Voto y 20 → 25 con Ascua, cambio de máscara a mitad de ataque, ciclo en ambos sentidos, recarga, lista vacía o de una máscara, cinto lleno, estado por IDs, HUD de máscara y una partida completa con muerte, caída, reactivación del punto, recogidas sin duplicar, encuentro, final y partida nueva.

```bash
"$GODOT" --headless --fixed-fps 60 --path . -s res://Tests/stage3_tests.gd
```

**Pruebas de la etapa 4.** Comprueban tema y glifos del español, buses de audio, colisionador simétrico, tiles en la cuadrícula, fundido y ambiente al entrar y salir del Atrio 2, brasero y poses del custodio por fase.

```bash
"$GODOT" --headless --fixed-fps 60 --path . -s res://Tests/stage4_tests.gd
```

**Pruebas de la etapa 5.** Comprueban:
- El contrato de la ruta: diez salas, salidas y llegadas, cinco puntos, IDs únicos, huecos ≤ 96 px y escalones ≤ 64 px.
- El recorrido completo del plano de entrada al epílogo.
- La muerte y la reaparición en cada punto de control.
- El acólito: daño, Voto, salto y cobertura.
- Los patrones, las ventanas de vulnerabilidad y la fase 2 del Abad.
- Una victoria contra el Abad con cada combinación de arma y máscara, jugada por un jugador simulado que sólo pulsa acciones del InputMap.
- Morir ante el Abad y repetir.

```bash
"$GODOT" --headless --fixed-fps 60 --path . -s res://Tests/stage5_tests.gd
```

Capturas de la campaña (necesita ventana): `"$GODOT" --path . -s res://tools/stage5_capture.gd`.

**Pruebas de la etapa 6.** Usan su propia carpeta (`user://tests_stage6/`) y comprueban:
- **Guardado:** primera ejecución, partida nueva guardada, guardado al encender un brasero, continuar, cerrar y reabrir, cargar dos veces seguidas.
- **Archivos problemáticos:** incompleto, con basura, de versión desconocida, con una sala o un objeto que ya no existen, escritura interrumpida y copia de seguridad.
- **Partida completada** y confirmación para sustituirla.
- **Pausa:** sin movimiento ni ataques, sin salto al reanudar con Espacio, tecla soltada en pausa, volver al brasero, muerte con la pausa abierta y sin pausa a mitad de un cambio de sala.
- **Ajustes** persistentes y archivo de ajustes dañado.
- **Navegación con teclado** por todos los menús.

```bash
"$GODOT" --headless --fixed-fps 60 --path . -s res://Tests/stage6_tests.gd
```

Capturas de los menús (necesita ventana): `"$GODOT" --path . -s res://tools/stage6_capture.gd`.

Tras añadir un `class_name` nuevo hay que importar una vez (`tools/smoke.sh` lo hace) antes de lanzar las pruebas.

Ninguna de estas comprueba la presentación visual: headless no dibuja.

## Godot AI (opcional)

El repositorio incluye el complemento **Godot AI 3.2.4** en `addons/godot_ai/`, activado como plugin del editor y con un autoload de depuración (`_mcp_game_helper`).

- **Para jugar o probar no hace falta.** El juego arranca sin el servidor MCP; el autoload se registra y queda inactivo.
- **Para usarlo con Claude Code** hace falta `uv` para instalar su servidor y, en el editor, **Godot AI → Claude Code → Configure**. Ver `addons/godot_ai/README.md`.
- **En CI**, importa con `--recovery-mode` (es lo que hace `tools/smoke.sh`): abre el proyecto sin iniciar los complementos del editor.
- **Al exportar**, el complemento trae un plugin de exportación que intenta retirar el autoload del paquete. Eso aún no está comprobado: se verifica con la build real en la etapa 7.
