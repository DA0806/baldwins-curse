# Inventario de assets y procedencias

Revisado el 16 de noviembre de 2026 sobre el commit `0f16a75`. **Pendiente** significa que el repositorio no documenta autor, fuente ni permiso de distribución: hay que confirmarlo con quien añadió el archivo o sustituirlo antes de distribuir una build.

| Archivo | Uso | Autor | Fuente | Permiso de distribución | Créditos | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| `Sprites/Characters/Knight_1/*.png` (12 hojas, celdas de 128×128) | Jugador hasta la etapa 4. **Sin uso desde la etapa 5** (sustituido por `Sprites/Characters/Baldwin/`) | Pendiente | Pendiente. Añadidas en el commit `0f16a75` | Pendiente | Pendiente | Sin uso: borrar o acreditar antes de distribuir |
| `Sprites/Items/Weapons/Copper_Sword.png` (64×64) | Icono de la espada hasta la etapa 4. **Sin uso desde la etapa 5** (sustituido por `Baldwin_Sword.png`) | Pendiente | Pendiente | Pendiente | Pendiente | Sin uso: borrar o acreditar antes de distribuir |
| `Sprites/Items/Weapons/Test_Mace.png` (64×64) | Icono y pickup de la maza de prueba | Generado para este proyecto en la etapa 2 (dibujo por código) | Este repositorio | Propio | — | Provisional: sustituir por arte final |
| `Sprites/Items/Masks/Mask_Vow.png`, `Mask_Ember.png` (64×64) | Iconos de las máscaras (óvalo y triángulo) | Generados para este proyecto en la etapa 3 (dibujo por código) | Este repositorio | Propio | — | Provisional: sustituir por arte final |
| Salas del circuito, llama del punto de control, reja y final | Bloques de color y figuras dibujadas por código (`BlockGeometry`, `Checkpoint`, `RoomExit`) | Este repositorio | Este repositorio | Propio | — | Provisional: arte en la etapa 4 |
| `Sprites/Environment/Atrio/*.png` (tiles de 16 px, fondo lejano y medio, candelabro, urna, lápida, estandarte, pedestal, púas, resplandor, arco de salida, brasero) | Sala de referencia Atrio 2 | Generados para este proyecto en la etapa 4 (`tools/gen_atrio_assets.py`) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Enemies/custodio.png` (4 poses de 96×48) | Enemigo del Atrio 2 | Generado en la etapa 4 (`tools/gen_atrio_assets.py`) | Este repositorio | Propio | — | Candidato a final; faltan cuadros intermedios |
| `Audio/amb_atrio.wav`, `sfx_attack.wav`, `sfx_hit.wav`, `sfx_pickup.wav`, `sfx_mask.wav` | Ambiente y efectos | Sintetizados en la etapa 4 (`tools/gen_atrio_assets.py`) | Este repositorio | Propio | — | Provisional: pulir o sustituir |
| `Themes/baldwin_ui.tres` | Tema de la interfaz | Este repositorio | Este repositorio | Propio | — | En uso |
| Fuente de la interfaz | Textos | Fuente por defecto incluida en Godot | Motor Godot | Licencia del motor (MIT) y la de la fuente incluida; por confirmar el texto de crédito | Por confirmar | Confirmar créditos antes de la 1.0 |
| `Sprites/Environment/Cripta/*.png` (tiles de 16 px, bg_far, bg_mid, niche_skulls, coffin, chain, candles), `Sprites/Environment/Capilla/*.png` (tiles de 16 px, bg_far, bg_mid, lectern, altar, statue), `Sprites/Environment/Common/inscription.png` | Zonas Cripta de las Ascuas y Capilla del Último Sello | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Enemies/acolito.png` (4×64×48), `ember_orb.png` (2×12×12), `custodio_sellado.png` (4×96×48) | Enemigos de la etapa 5 | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Bosses/abad.png` (9×224×128), `falling_ember.png` (2×16×32), `ember_marker.png` (32×8) | Jefe: el Abad Sellado y sus ataques | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Characters/Baldwin/*.png` (Idle, Walk, Jump, Attack, Dead, Hurt; celdas de 128×128) | Jugador (Baldwin); sustituye a `Sprites/Characters/Knight_1/` | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Items/Weapons/Crypt_Mace.png`, `Baldwin_Sword.png` (64×64) | Iconos de la Maza de la Cripta y de la espada de Baldwin | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Story/intro.png`, `epilogue.png` (640×360) | Ilustraciones de introducción y epílogo | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Audio/amb_cripta.wav`, `amb_capilla.wav`, `boss_loop.wav`, `sfx_throw.wav`, `sfx_tell_sweep.wav`, `sfx_tell_rain.wav`, `sfx_roar.wav`, `sfx_checkpoint.wav`, `sfx_ember_impact.wav` | Ambientes, música del jefe y efectos de la etapa 5 | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Provisional: sintetizado, sin revisar a oído |
| Enemigo terrestre (salas provisionales y laboratorio) y maniquí | Rectángulos de color definidos en `Scenes/Enemies/*.tscn`, sin archivos de imagen | Este repositorio | Este repositorio | Propio | — | Provisional: falta arte de enemigos |
| `Shaders/ItemShineHighlight.gdshader` | Brillo de los pickups | Pendiente. Los comentarios de `Scripts/ItemPickup.gd` hablan de un "ejemplo original", así que puede venir de un shader publicado | Pendiente | Pendiente | Pendiente | **Pendiente** |
| `icon.svg` | Icono del proyecto | Godot Engine (icono por defecto de un proyecto nuevo) | Plantilla de proyecto de Godot | Por confirmar si se distribuye; conviene sustituirlo por un icono propio | — | Sustituir antes de la 1.0 |
| `addons/godot_ai/` | Herramienta de desarrollo, no forma parte del juego | Godot AI (v3.2.4) | Incluido en el repositorio | MIT (`addons/godot_ai/LICENSE`) | Según la licencia MIT si se redistribuye | Acreditado; debe quedar fuera del paquete del juego |
| Escenas, scripts y recursos `.tres` propios | Juego | Autores del repositorio (DA0806, Diego Arau Andreu, según el historial) | Este repositorio | El repositorio no incluye un archivo de licencia | — | Propio |

## Lo que falta en el árbol

Fuente pixel propia, cuadros intermedios de animación (enemigos y caída de Baldwin) y una revisión a oído del audio sintetizado. El shader de brillo sigue con procedencia pendiente.

## Regla para las siguientes etapas

Cada archivo nuevo de arte o audio entra con su fila en esta tabla (autor, fuente, licencia y texto de crédito). Los archivos con procedencia pendiente sirven para prototipar, pero no cuentan como candidatos a final hasta acreditarlos.

## Modelos generados con Meshy (sustituyen a la sala de referencia)

Generados el 17 de noviembre de 2026 con Meshy (texto a 3D con textura, 300 créditos) desde la cuenta del usuario. Los modelos `.glb`, sus miniaturas y los IDs de tarea están en `Art/Meshy/` (`kit_tasks.json`); Godot no los importa (`.gdignore`). Se renderizan con un proyecto auxiliar de Godot (cámara ortográfica, fondo transparente) y `tools/meshy_to_sprites.py` los convierte en sprites (recorte, reducción, paleta de la guía, contorno) y los instala con `--install`.

| Archivo | Modelo de Meshy | Notas |
| --- | --- | --- |
| `Sprites/Enemies/custodio.png` | `custodio` | Modelo estático: las 4 poses son el cuerpo inclinado más la hoja dibujada encima. Poses reales necesitarían rigging y animación |
| `Sprites/Environment/Atrio/brazier.png` | `brasero` | Cuadro 0 con las brasas en ceniza y cuadros 1–3 con parpadeo |
| `Sprites/Environment/Atrio/arch_exit.png` | `arco_salida` | Hueco encendido y chevrón añadidos al pixelar; el arco es más bajo que la zona de salida |
| `Sprites/Environment/Atrio/candelabra.png` (24×32), `urn.png`, `tomb.png`, `pedestal.png` | `candelabro`, `urna`, `lapida`, `pedestal` | |
| `Sprites/Environment/Atrio/banner.png` (32×32) | `estandarte` | La flecha del modelo apunta arriba; chevrón hacia la salida añadido |
| `Sprites/Items/Masks/Mask_Vow.png`, `Mask_Ember.png` | `mascara_voto`, `mascara_ascua` | El Ascua es de acero oscuro con ojos de brasa |

**Licencia: pendiente.** Los derechos de uso dependen del plan de Meshy de la cuenta que los generó; hay que confirmarlo antes de distribuir una build. `tools/gen_atrio_assets.py` sigue generando las versiones anteriores dibujadas por código: ejecutarlo sobrescribe estos sprites, y después hay que volver a correr `python3 tools/meshy_to_sprites.py --install`.

## Lote de personajes prerenderizados · 17 de noviembre de 2026

Lote nuevo con cuatro referencias, cuatro modelos Meshy t2.5/n1 (objetivo de 12 000 polígonos), cuatro rigs y cuatro clips adicionales de Baldwin. Consumo registrado: 128 créditos Meshy (36 referencias, 60 modelos, 20 rigging, 12 clips). Los IDs de generación están en `Art/Meshy/prerendered/manifest.json`; los resultados de rigging/animación, en `rigs/*/meta.json` y `rigs/baldwin/actions/meta.json`. Las fuentes 3D están descargadas localmente, con huellas en [arte_prerenderizado.md](arte_prerenderizado.md).

`tools/render_characters.py` renderiza huesos e IK en Blender 4.5.9; el equipo se modela localmente. `tools/pack_prerendered.py` convierte los renders a diez hojas/52 cuadros con la paleta de la guía. **Estado: primera pasada de render producida, con correcciones en curso; integración y QA final pendientes.** Las filas anteriores conservan la procedencia histórica de las versiones previas; no prueban los derechos del lote nuevo.

| Archivo o grupo | Uso | Autor / elaboración | Fuente | Permiso de distribución | Créditos | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| `Art/Meshy/prerendered/references/`, `models/`, `rigs/` | Fuentes del lote de personajes | Generación con Meshy desde la cuenta del usuario; dirección artística del proyecto | IDs y prompts en `manifest.json`; metadatos de tareas en `rigs/` | Pendiente de comprobar según plan y términos aplicables | Meshy; texto final de crédito pendiente | Fuentes generadas y descargadas |
| `Art/Meshy/prerendered/sprites/Characters/Baldwin/*.png` → `Sprites/Characters/Baldwin/*.png` | Baldwin: Idle, Walk, Jump, Attack, Dead y Hurt | Modelo/rig/clips Meshy, poses y equipo locales, render Blender y conversión del proyecto | Lote Baldwin; recetas `render_characters.py` y `pack_prerendered.py` | Pendiente para el material derivado de Meshy | Según derechos confirmados | Pendiente de integración final; Hurt sigue sin uso en runtime |
| `Art/Meshy/prerendered/sprites/Enemies/custodio.png`, `custodio_sellado.png` → `Sprites/Enemies/` | Custodio y variante sellada | Modelo y rig Meshy compartidos; cuatro poses óseas por variante; sello, ataduras y espada locales | Lote custodio | Pendiente para el material derivado de Meshy | Según derechos confirmados | Pendiente de integración final |
| `Art/Meshy/prerendered/sprites/Enemies/acolito.png` → `Sprites/Enemies/acolito.png` | Acólito y sus cuatro poses | Modelo/rig Meshy; poses óseas, IK e incensario local | Lote acólito | Pendiente para el material derivado de Meshy | Según derechos confirmados | Pendiente de integración final |
| `Art/Meshy/prerendered/sprites/Bosses/abad.png` → `Sprites/Bosses/abad.png` | Abad y sus nueve estados | Modelo/rig Meshy; poses óseas, IK, guadaña, incensario y sello locales | Lote Abad | Pendiente para el material derivado de Meshy | Según derechos confirmados | Pendiente de integración final |

Los iconos, proyectiles y fondos conservan sus procedencias anteriores salvo sustitución explícitamente registrada. No regenerar los sprites con herramientas legadas después de instalar este lote: podrían sobrescribirlo. La existencia de modelos, renders o pruebas funcionales no resuelve licencias pendientes ni demuestra una revisión visual completa.
