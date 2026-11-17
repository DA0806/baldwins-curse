# Manifiesto de assets de la etapa 5

Generado por `tools/gen_zone_assets.py` (dibujo y síntesis por código con Pillow y numpy; semillas fijas; sin archivos de terceros ni servicios externos). Este archivo lo reescribe el propio script.

Todos los personajes miran a la derecha; el juego los voltea. Las hojas son tiras horizontales de cuadros del mismo tamaño.

## Imágenes

| Archivo | Medida | Cuadros | Uso |
| --- | --- | --- | --- |
| `Sprites/Environment/Cripta/floor_top.png` | 16×16 | 1 | Borde superior pisable de la Cripta |
| `Sprites/Environment/Cripta/floor_fill.png` | 16×16 | 1 | Relleno en mosaico de la Cripta |
| `Sprites/Environment/Cripta/platform.png` | 16×16 | 1 | Losa de plataforma de la Cripta |
| `Sprites/Environment/Cripta/bg_far.png` | 640×360 | 1 | Fondo lejano opaco (mosaico horizontal, periodo 160) |
| `Sprites/Environment/Cripta/bg_mid.png` | 640×360 | 1 | Plano medio con transparencia (mosaico horizontal, periodo 128) |
| `Sprites/Environment/Cripta/niche_skulls.png` | 32×32 | 1 | Utilería: nicho de calaveras |
| `Sprites/Environment/Cripta/coffin.png` | 32×16 | 1 | Utilería: ataúd |
| `Sprites/Environment/Cripta/chain.png` | 8×64 | 1 | Utilería: cadena colgante |
| `Sprites/Environment/Cripta/candles.png` | 16×16 | 1 | Utilería: velas en el suelo |
| `Sprites/Environment/Capilla/floor_top.png` | 16×16 | 1 | Borde superior pisable de la Capilla (mármol) |
| `Sprites/Environment/Capilla/floor_fill.png` | 16×16 | 1 | Relleno en mosaico de la Capilla |
| `Sprites/Environment/Capilla/platform.png` | 16×16 | 1 | Losa de plataforma de la Capilla |
| `Sprites/Environment/Capilla/bg_far.png` | 640×360 | 1 | Nave con vitrales apagados (mosaico, periodo 160) |
| `Sprites/Environment/Capilla/bg_mid.png` | 640×360 | 1 | Columnas de mármol (mosaico, periodo 128) |
| `Sprites/Environment/Capilla/lectern.png` | 16×32 | 1 | Utilería: atril |
| `Sprites/Environment/Capilla/altar.png` | 48×32 | 1 | Utilería: altar |
| `Sprites/Environment/Capilla/statue.png` | 32×64 | 1 | Utilería: estatua de caballero |
| `Sprites/Environment/Common/inscription.png` | 32×24 | 1 | Lápida o placa con runas marfil |
| `Sprites/Enemies/acolito.png` | 256×48 | 4 | Acólito de la Ascua: hoja 4x64x48; origen (32,24), pies fila 47; mano de lanzamiento en el cuadro 2 hacia (46,16) |
| `Sprites/Enemies/ember_orb.png` | 24×12 | 2 | Proyectil del acólito: hoja 2x12x12 (el segundo cuadro parpadea) |
| `Sprites/Enemies/custodio_sellado.png` | 384×48 | 4 | Custodio sellado: hoja 4x96x48; origen (48,24), pies fila 47; golpe de x 54 a 90 |
| `Sprites/Bosses/abad.png` | 2016×128 | 9 | Abad Sellado: hoja 9x224x128; origen (112,64), pies fila 120 |
| `Sprites/Bosses/falling_ember.png` | 32×32 | 2 | Brasa que cae: hoja 2x16x32 |
| `Sprites/Bosses/ember_marker.png` | 32×8 | 1 | Marca de aviso en el suelo |
| `Sprites/Items/Weapons/Crypt_Mace.png` | 64×64 | 1 | Icono de la Maza de la Cripta |
| `Sprites/Items/Weapons/Baldwin_Sword.png` | 64×64 | 1 | Icono de la espada de Baldwin |
| `Sprites/Story/intro.png` | 640×360 | 1 | Ilustración de introducción (franja superior libre para texto) |
| `Sprites/Story/epilogue.png` | 640×360 | 1 | Ilustración del epílogo |
| `Sprites/Characters/Baldwin/Idle.png` | 512×128 | 4 | Baldwin, reposo (celdas 128x128, pies fila 127, centro columna 32) |
| `Sprites/Characters/Baldwin/Walk.png` | 1024×128 | 8 | Baldwin, andar |
| `Sprites/Characters/Baldwin/Jump.png` | 768×128 | 6 | Baldwin, salto |
| `Sprites/Characters/Baldwin/Attack.png` | 640×128 | 5 | Baldwin, ataque (0-3 anticipación, 4 tajo con estela en x 38-92, filas 76-116) |
| `Sprites/Characters/Baldwin/Dead.png` | 768×128 | 6 | Baldwin, muerte |
| `Sprites/Characters/Baldwin/Hurt.png` | 256×128 | 2 | Baldwin, daño |

## Audio (WAV mono, 16 bits, 44,1 kHz; pico en torno a −1 dBFS)

| Archivo | Duración | Pico | Uso |
| --- | --- | --- | --- |
| `Audio/amb_cripta.wav` | 8.000 s | -1.0 dBFS | Ambiente de la Cripta (bucle de 8 s) |
| `Audio/amb_capilla.wav` | 8.000 s | -1.0 dBFS | Ambiente de la Capilla (bucle de 8 s) |
| `Audio/boss_loop.wav` | 8.000 s | -1.0 dBFS | Música del jefe (bucle de 8 s) |
| `Audio/sfx_throw.wav` | 0.400 s | -1.0 dBFS | Lanzamiento del acólito |
| `Audio/sfx_tell_sweep.wav` | 0.600 s | -1.0 dBFS | Aviso del tajo (chirrido metálico ascendente) |
| `Audio/sfx_tell_rain.wav` | 0.800 s | -1.0 dBFS | Aviso de la lluvia (campana) |
| `Audio/sfx_roar.wav` | 0.800 s | -1.0 dBFS | Rugido del cambio de fase |
| `Audio/sfx_checkpoint.wav` | 0.700 s | -1.0 dBFS | Brasero que se enciende |
| `Audio/sfx_ember_impact.wav` | 0.300 s | -1.0 dBFS | Brasa contra el suelo |

Los bucles de 8 s se generan con ruido periódico, frecuencias de ciclos enteros y colas plegadas sobre el inicio, de modo que cierran sin chasquido. Al estar los bucles normalizados al mismo pico que los efectos, conviene bajar su `volume_db` en el bus Music.

## Notas de integración

- Acólito: la mano que lanza está en (46,16) del cuadro 2 (cuadro de 64×48, origen en (32,24)). El cuadro 1 lleva el incensario sobre la cabeza.
- Abad: el cuadro 2 barre de x 112 a x 208 entre las filas 96 y 120; los cuadros 3 y 6 tienen el sello brillando (vulnerable); los cuadros 1 y 4 son poses claramente distintas (guadaña atrás y en alto frente a incensario sobre la cabeza).
- Baldwin: celdas de 128×128; pies en la fila 127 y centro del cuerpo en la columna 32 en todos los cuadros (en Jump, el pie más bajo toca la fila 127 aunque el personaje esté en el aire; en Dead 3-5 el cuerpo rota y queda tumbado sobre la fila 127). La estela del cuadro 4 de Attack cubre x 38-92, filas 76-116.
- `platform.png` (Cripta y Capilla) es opaco en los 16×16; `bg_mid.png` de ambas zonas tiene transparencia.

## Filas para `docs/assets.md`

Columnas: Archivo | Uso | Autor | Fuente | Permiso de distribución | Créditos | Estado.

| Archivo | Uso | Autor | Fuente | Permiso de distribución | Créditos | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| `Sprites/Environment/Cripta/*.png` (tiles de 16 px, bg_far, bg_mid, niche_skulls, coffin, chain, candles), `Sprites/Environment/Capilla/*.png` (tiles de 16 px, bg_far, bg_mid, lectern, altar, statue), `Sprites/Environment/Common/inscription.png` | Zonas Cripta de las Ascuas y Capilla del Último Sello | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Enemies/acolito.png` (4×64×48), `ember_orb.png` (2×12×12), `custodio_sellado.png` (4×96×48) | Enemigos de la etapa 5 | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Bosses/abad.png` (9×224×128), `falling_ember.png` (2×16×32), `ember_marker.png` (32×8) | Jefe: el Abad Sellado y sus ataques | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Characters/Baldwin/*.png` (Idle, Walk, Jump, Attack, Dead, Hurt; celdas de 128×128) | Jugador (Baldwin); sustituye a `Sprites/Characters/Knight_1/` | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Items/Weapons/Crypt_Mace.png`, `Baldwin_Sword.png` (64×64) | Iconos de la Maza de la Cripta y de la espada de Baldwin | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Sprites/Story/intro.png`, `epilogue.png` (640×360) | Ilustraciones de introducción y epílogo | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
| `Audio/amb_cripta.wav`, `amb_capilla.wav`, `boss_loop.wav`, `sfx_throw.wav`, `sfx_tell_sweep.wav`, `sfx_tell_rain.wav`, `sfx_roar.wav`, `sfx_checkpoint.wav`, `sfx_ember_impact.wav` | Ambientes, música del jefe y efectos de la etapa 5 | Generado para este proyecto en la etapa 5 (tools/gen_zone_assets.py) | Este repositorio | Propio | — | Candidato a final |
