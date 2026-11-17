# Etapa 4 · Sala de referencia (Atrio 2)

El Atrio 2 es la sala con arte y sonido de referencia. Conserva la geometría y las reglas de la etapa 3 (mismos bloques, foso de 96 px, brasero en x 150, Ascua en x 700, custodio en x 1020, salida en x 1256). Las salas 1 y 3 siguen con arte provisional hasta la etapa 5.

## Qué hay en la sala

| Elemento | Recurso |
| --- | --- |
| Suelo y muros | `floor_top.png` + `floor_fill.png`, tiles de 16 px dibujados sobre el mismo rectángulo que colisiona |
| Fondo por planos | `bg_far.png` (desplazamiento 0,2) y `bg_mid.png` (0,5) con `Parallax2D` |
| Punto de control | Brasero `brazier.png`: apagado y llama animada al activarse |
| Enemigo | Custodio `custodio.png`, una pose por fase de ataque |
| Objeto | Máscara de Ascua sobre `pedestal.png` |
| Peligro | Foso con `spikes.png` y `pit_glow.png` |
| Salida | Arco `arch_exit.png` y dos estandartes `banner.png` con chevrones |
| Utilería | Candelabros, urnas y lápidas |
| Audio | Ambiente `amb_atrio.wav` (bus Music) que entra y sale con fundido; efectos de ataque, impacto, recogida y máscara (bus SFX) |
| Transición | Fundido a negro de 0,25 s en cada cambio de sala |

Arte y audio son propios y salen de `tools/gen_atrio_assets.py`. Reglas en [../arte.md](../arte.md) y procedencias en [../assets.md](../assets.md).

## Capturas (juego detenido)

En `capturas/`, cada escena en cuatro versiones: `NN_nombre.png` (640×360), `_x2` (1280×720), `_x3` (1920×1080) y `_gris` (escala de grises). La hoja `hoja_grises.png` reúne las cinco en grises.

| Captura | Qué debe distinguirse |
| --- | --- |
| `01_brasero_foso` | Brasero encendido, suelo pisable frente al vacío y púas del foso |
| `02_foso_pickup` | Peligro (púas) frente a objeto (máscara sobre pedestal) |
| `03_anticipacion` | Custodio con la hoja alzada, `!` y ojos encendidos |
| `04_golpe` | Hoja extendida sobre el jugador, que recibe el golpe |
| `05_salida` | Arco encendido con chevrones y estandartes que apuntan a la salida |

Las versiones ×2 y ×3 son la ampliación entera por vecino más cercano del render de 640×360, que es lo que hace el proyecto (stretch `viewport`, escala entera).

## Grabación

`grabacion_atrio.mp4`: 32 s, 1280×720, 30 fps, H.264 con audio AAC. El recorrido es guiado por entradas del InputMap. Incluye:

- Fundido de entrada desde el Atrio 1 con el ambiente apareciendo.
- Activación del brasero.
- Caída al foso y vuelta al brasero.
- Salto largo.
- Recogida del Ascua y cambios de máscara con la recarga en el HUD.
- Anticipación y golpe del custodio con el Voto.
- Una esquiva de la segunda anticipación.
- Combate con el Ascua.
- Salida al Atrio 3 con el ambiente apagándose.

## Cómo reproducirlo

```bash
python3 tools/gen_atrio_assets.py
```

```bash
"$GODOT" --path . -s res://tools/stage4_capture.gd
```

```bash
python3 tools/stage4_sheets.py
```

```bash
"$GODOT" --path . --write-movie /tmp/atrio/f.png -s res://tools/stage4_demo.gd
```

```bash
swift tools/frames_to_mp4.swift /tmp/atrio /tmp/atrio/f.wav docs/etapa4/grabacion_atrio.mp4
```

La captura y la grabación necesitan ventana (no headless). La carpeta `docs/etapa4/` tiene un `.gdignore` para que Godot no importe estas imágenes.

## Candidatos a final y sustituciones

| Recurso | Estado |
| --- | --- |
| Tiles, fondos, utilería, brasero, arco, estandartes, púas | Candidatos a final (propios); revisar en una partida a mano |
| Custodio | Candidato a final para el enemigo básico; le faltan cuadros intermedios de animación |
| Audio sintetizado | Candidato provisional: sirve para la referencia, conviene sustituirlo o pulirlo con un diseñador de sonido |
| Caballero del jugador, espada de cobre, shader de brillo | **Procedencia pendiente**: hay que acreditarlos o sustituirlos antes de distribuir (ver `docs/assets.md`) |
| Iconos de máscaras y maza | Provisionales (etapas 2 y 3) |

## Pendiente de comprobar con el editor o en otra máquina

- Ver el juego en una pantalla real de **1920×1080** y en Windows: aquí las versiones ×3 se calcularon ampliando la captura. La pantalla de este Mac no admite una ventana de 1080p.
- Escuchar la mezcla con altavoces: niveles relativos de ambiente y efectos (−4 dB Music, −2 dB SFX) y la costura del bucle de 8 s.
- Revisar en el editor las uniones de los tiles en los bordes del foso a ×3.
