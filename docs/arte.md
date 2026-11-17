# Guía de arte · Baldwin's Curse

Abadía funeraria en pixel art. Esta guía fija las reglas con las que se hizo la sala de referencia (Atrio 2, etapa 4) y con las que se vestirán las demás salas en la etapa 5. El kit actual sale de `tools/gen_atrio_assets.py` (dibujo por código, sin recursos de terceros).

## Resolución y escala

- Viewport de **640×360**, filtro **nearest** (`default_texture_filter=0`), stretch `viewport` con escala **entera**.
- Objetivos: 1280×720 (×2) y 1920×1080 (×3). Nada se dibuja a media escala ni con filtrado.
- Cuadrícula de **16 px**. Los bloques de colisión empiezan y miden múltiplos de 16 en x, y su borde superior cae en la cuadrícula.

## Paleta

| Nombre | Hex | Uso |
| --- | --- | --- |
| Fondo | `#151924` | Cielo, vacío, rostro del custodio |
| Fondo lejano | `#1C2230` | Masa de la abadía al fondo |
| Piedra oscura | `#232B37` | Columnata media, relleno de muros |
| Piedra | `#303B4A` | Ladrillo del plano de juego, túnicas |
| Piedra clara | `#3E4B5E` | Capucha, arco de salida |
| Acero | `#6D8297` | Metal, contorno de siluetas, borde de barras |
| Marfil | `#E5D6B3` | Texto, filos, chevrones de ruta, cera |
| Cobre | `#B96A47` | Objetos, estandartes, barra de salud |
| Brasa | `#F0A758` | Lo que está activo: llama encendida, ojos en anticipación, interior de la salida, borde del HUD |

Regla: cuanto más cálido y claro, más importante. El fondo nunca usa cobre ni brasa salvo las ventanas lejanas, muy apagadas (`#3A2A22`).

## Planos y contraste

| Plano | Desplazamiento | Valores |
| --- | --- | --- |
| Lejano (`bg_far`) | 0,2 | Los más oscuros |
| Medio (`bg_mid`, columnata) | 0,5 | Oscuros, con un canto iluminado |
| Utilería (candelabros, urnas, lápidas) | 1 | Medios; detrás del jugador (`z_index -1`) |
| Juego (suelo, jugador, enemigos, objetos) | 1 | Los más claros y saturados |
| HUD | fijo | Marfil sobre negro translúcido, contorno de 3 px en los textos |

El suelo pisable lleva una línea marfil gastada y otra de acero en su borde superior: la superficie que se ve es la que colisiona (`BlockGeometry` dibuja y colisiona con el mismo rectángulo).

## Siluetas y pivote

- Pivote a los pies, en el centro del colisionador. El jugador usa celdas de 128×128 con el pie en la columna 32 y la fila 96 de la celda. Su colisionador (24×64) y sus rayos de esquina son simétricos respecto al pivote, de modo que al girar no se desplaza.
- El custodio usa cuadros de 96×48 con origen en el centro: los pies quedan en +24, igual que el fondo de su colisionador.
- Contorno de acero de 1 px por arriba y a los lados en los personajes oscuros, para que no se pierdan contra la columnata.

## Anticipación, golpe y recuperación

Cada ataque enemigo tiene una pose distinta por fase, legible sin color:

1. **Reposo:** hoja baja hacia delante.
2. **Anticipación (0,5 s):** hoja vertical por encima de la cabeza, destello marfil en la punta, ojos de brasa y `!` encima.
3. **Golpe:** hoja horizontal con estela marfil. Ocupa exactamente la zona de golpe (de 6 a 42 px del centro).
4. **Recuperación:** cuerpo encorvado, hoja clavada en el suelo y ojos apagados.

El enemigo se dibuja por encima del jugador (`z_index 1`): la información de peligro nunca queda tapada.

## Lectura sin color y sin sonido

| Qué | Forma | Color | Sonido |
| --- | --- | --- | --- |
| Superficie pisable | Borde superior claro, ladrillo | Marfil y acero | — |
| Peligro (foso) | Púas | Puntas de brasa, resplandor de cobre | — |
| Anticipación enemiga | Hoja alzada, `!`, destello | Ojos de brasa | — |
| Golpe recibido | Empuje hacia atrás | Destello rojo | Impacto grave |
| Objeto recogible | Pedestal, brillo que barre el icono, aviso `[R]` | Cobre o marfil | Dos notas al recogerlo |
| Punto de control | La llama crece al encenderse | Brasa | — |
| Salida | Arco apuntado con chevrones `»` y estandartes que apuntan a ella | Interior de brasa | Fundido del ambiente |
| Máscara activa | Óvalo (Voto) o triángulo (Ascua), nombre y efecto | Marfil o cobre | Barrido vítreo al cambiar |

El sonido sólo refuerza: ninguna decisión depende de oírlo. Las capturas en grises de `docs/etapa4/` lo comprueban.

## HUD

- Arriba a la izquierda, la barra de salud: relleno de cobre y borde de acero.
- Abajo a la izquierda, las ranuras de arma y la de máscara: borde de brasa, la ranura de intercambio a pleno brillo y la otra atenuada. Junto a ellas, el nombre y el efecto de la máscara y una barra de recarga que se vacía. El icono se apaga mientras recarga.
- Tema `Themes/baldwin_ui.tres`: texto marfil con contorno de 3 px del color de fondo. La fuente es la de Godot y cubre los glifos del español (`á é í ó ú ü ñ ¿ ¡ « » —`); `Tests/stage4_tests.gd` lo comprueba.

## Partículas, luz y destellos

- Todavía no hay partículas. Cuando las haya: nunca deben tapar una zona de golpe, duran 0,3 s como máximo en impactos y se reducen con la opción de efectos reducidos de la etapa 6.
- La luz se pinta en el sprite (llamas, brasa del interior de la salida). No se usan luces 2D dinámicas en la etapa 4.
- Los destellos de daño duran lo que la invulnerabilidad (0,6 s) y nunca parpadean más de 3 veces por segundo.

## Audio

| Bus | Contenido |
| --- | --- |
| Music | Ambiente de sala (bucle de 8 s). Al cambiar de sala se cruza con fundido: si la sala nueva tiene el mismo ambiente sigue sonando, si es otro o ninguno se apaga en 0,4 s y el nuevo entra en 0,8 s |
| SFX | Ataque, impacto (más grave cuando lo recibe el jugador), recogida, cambio de máscara |

Los cambios de sala funden a negro en 0,25 s.
