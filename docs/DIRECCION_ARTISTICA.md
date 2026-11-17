# Baldwin's Curse — Dirección artística

> **Guía artística de trabajo / documento vivo** · 17 de noviembre de 2026.  
> Basada en [docs/arte.md](arte.md), los sprites, escenas y herramientas del repositorio. No sustituye automáticamente decisiones de arte existentes: **[Base]** es una regla ya documentada, **[Propuesta]** es un criterio recomendado y **[Pendiente]** requiere aprobación o validación.

## 1. Visión creativa

**Concepto rector:** *La última brasa de una abadía condenada.*

El jugador debe sentir que atraviesa una institución sagrada y funeraria donde el tiempo se detuvo, los votos se convirtieron en cadenas y el fuego de los sellos mantiene el sufrimiento. El mundo pertenece a la piedra, el humo y el silencio; la brasa cálida revela aquello que sigue activo: una amenaza, un juramento, un recuerdo, una salida o un punto de descanso.

**Identidad actual [Base]:** fantasía gótica funeraria, pixel art 2D, tres zonas de la abadía, siluetas de guerreros y clérigos, símbolos de juramento y fuego. El material actual usa paleta fría de piedra/acero contra señales cálidas de cobre, marfil y brasa.

**Dirección emocional [Propuesta]:** austeridad antes que espectacularidad; misterio antes que horror; un mundo hostil pero legible. La estética no debería depender de sangre, jumpscares, saturación constante, partículas densas ni detalles microscópicos ilegibles a 640×360.

### Tres reglas maestras

1. **Lo cálido significa algo.** Usar brasa/cobre para acciones, sellos, amenazas y lugares de interacción; no dispersarlos al azar en el fondo.
2. **La silueta explica el combate.** El arma alzada, el cuerpo inclinado y las marcas del suelo han de comunicar qué hará el enemigo incluso en escala de grises.
3. **La arquitectura cuenta la historia.** Atrio = juramento; Cripta = retención de almas; Capilla = autoridad y último sello. Repetir símbolos con variaciones que revelen la progresión.

## 2. Moodboard verbal y palabras clave

**Materiales:** piedra húmeda, mampostería gastada, hierro ennegrecido, cobre envejecido, cera, tela pesada, ceniza y mármol frío.  
**Arquitectura:** arcadas ojivales, columnas, nichos funerarios, lápidas, estandartes, altares, grandes puertas y vitrales apagados.  
**Iluminación:** penumbra fría, rim light de acero, pequeños puntos de luz marfil y brasa.  
**Ambiente:** quietud, gravedad, soledad, solemnidad y una liberación lenta hacia la luz del amanecer.

**Evitar [Propuesta]:** neón puro, efectos holográficos, formas sci-fi, interfaces modernas saturadas, fantasía genérica demasiado ornamentada, luces uniformes que aplanen la escena o ruido visual que compita con los hitboxes.

### Referentes de lenguaje visual, no de copia

Priorizar fotografía/ilustración de ruinas góticas, relieves de piedra, vitrales medievales y estudio de siluetas con animación 2D; cualquier referencia a videojuegos u obras ajenas debe usarse sólo para analizar lectura, ritmo o composición, nunca para replicar diseños propietarios.

## 3. Paleta oficial de partida [Base]

Los siguientes colores se toman literalmente de docs/arte.md:

| Token | Hex | Uso principal |
| --- | --- | --- |
| Fondo | **#151924** | Vacío, cielo, huecos negros y contraste de interfaz |
| Fondo lejano | **#1C2230** | Masa arquitectónica más distante |
| Piedra oscura | **#232B37** | Muros medios, sombras profundas |
| Piedra | **#303B4A** | Plano jugable, túnicas, estructuras |
| Piedra clara | **#3E4B5E** | Bisel de columna, capucha, borde del arco |
| Acero | **#6D8297** | Bordes de silueta, armas, contorno de barras |
| Marfil | **#E5D6B3** | Texto, filos, pista de ruta, cera |
| Cobre | **#B96A47** | Pickups, estandartes, salud |
| Brasa | **#F0A758** | Amenaza activa, fuego, ojos, énfasis y foco |

**Valores adicionales que ya aparecen en el pipeline Meshy:** #A99C80 (marfil envejecido), #7A3A22 (cobre oscuro), #FFD59A (núcleo de llama) y #3A2A22 (ventana lejana cálida atenuada). Tratarlos como tonos auxiliares, no como sustitutos de los tokens principales.

### Jerarquía cromática [Base + Propuesta]

- **Plano lejano:** 70–90 % del peso visual en fríos oscuros; nada de brasa intensa salvo focos muy aislados.
- **Plano medio:** contraste moderado de piedra con bordes de acero apagado.
- **Plano jugable:** la mayor nitidez, contornos y acentos de silueta.
- **Elementos interactivos:** cobre/marfil con brillo breve, icono, forma o texto.
- **Peligro / ataque activo:** brasa intensa, señal geométrica y animación contextual.
- **Interfaz:** texto marfil sobre fondo oscuro con contorno fuerte; foco de menú en brasa.

Los porcentajes son una pauta compositiva **[Propuesta]**, no mediciones ni limitaciones implementadas.

### Color como sistema semántico

| Significado | Color orientativo | Señal de forma obligatoria |
| --- | --- | --- |
| Piso seguro | Piedra + borde marfil/acero | Borde horizontal y bloque sólido |
| Hueco peligroso | Oscuro + puntas cálidas | Púas y vacío reconocibles |
| Anticipación | Brasa y destello marfil | Arma elevada, postura distinta y «!» |
| Pickup | Cobre o marfil | Pedestal, icono y aviso de interacción |
| Guardado / descanso | Brasa | Brasero que cambia de apagado a encendido |
| Salida | Luz cálida | Arco y chevrones direccionales |
| Voto | Marfil | Óvalo |
| Ascua | Cobre / brasa | Triángulo |
| Jefe vulnerable | Núcleo marfil / brasa | Sello del pecho encendido y pose de recuperación |

No utilizar color como único canal de comunicación.

## 4. Resolución, retícula y dibujo [Base]

- Viewport lógico **640 × 360**.
- Presentación prevista **1280 × 720 (×2)** y **1920 × 1080 (×3)**, siempre en escala entera.
- Filtro **nearest-neighbor**; no utilizar bilinear, blur ni desplazamientos semipíxel en sprites de gameplay.
- Geometría y tiles con cuadrícula base de **16 × 16 píxeles**; la superficie visual de apoyo debe coincidir con la colisión.
- Para UI y textos, validar el render original antes de escalar: detalles bonitos en 3× pueden resultar invisibles a 1×.

### Disciplina de pixel art [Propuesta]

- Construir masas grandes y siluetas primero; añadir texturas sólo donde ayudan a explicar material o volumen.
- Mantener clusters de píxeles coherentes; evitar grano independiente de un píxel repartido sin control.
- Preferir 2–4 niveles de luz por material, derivados de la paleta, sobre gradientes fotográficos.
- Reservar los blancos más claros y naranjas más luminosos para objetivos de atención.
- Dibujar con intención las diagonales de armas, púas y chevrones para conservar su lectura.
- Usar sombras estructurales, no un halo brillante alrededor de absolutamente todo.

## 5. Capas, cámara, materiales y composición [Base]

| Capa | Parallax / z | Tratamiento |
| --- | --- | --- |
| Fondo lejano, bg_far | scroll_scale 0,2 | Siluetas muy oscuras, poco detalle |
| Fondo medio, bg_mid | scroll_scale 0,5 | Columnata y arquitectura secundaria |
| Utilería | velocidad 1, z_index -1 | Objetos reconocibles detrás del jugador |
| Mundo jugable | velocidad 1 | Suelo, protagonista, enemigos, pickups; máximo contraste |
| Amenazas delanteras | z_index de enemigo superior al jugador en casos necesarios | Jamás ocultar la anticipación |
| HUD | fijo en pantalla | Claridad por encima de atmósfera |

### Regla de encuadre [Propuesta]

En cada pantalla, el jugador debe localizar en menos de un instante: **(a)** dónde puede pisar, **(b)** qué amenaza se mueve, **(c)** cuál es el siguiente objetivo interactivo y **(d)** dónde está la salida cuando corresponde. Evitar colocar utilería ornamentada exactamente detrás de un arma durante la anticipación.

La cámara está acotada por sala; las propuestas artísticas deben funcionar en desplazamiento lateral real, no únicamente en un screenshot estático.

## 6. Identidad de las tres zonas

### Atrio del Voto — Juramento

**Estado existente:** primera zona con piedra, arcadas, estandartes, pedestal, urnas, lápidas, brasero, foso, púas y custodios. Atrio 2 sirve como sala de referencia.

**Dirección [Propuesta]:** espacios más abiertos, arquitectura disciplinada y estandartes aún reconocibles. Sensación de orden degradado: el lugar muestra *lo que el juramento intentó proteger*. Contraste suficiente para enseñar las reglas. El Voto se introduce aquí y debe tener lectura visual distinta de la Ascua.

**Motivos:** óvalo, cera, metal de guardia, símbolos de custodia, arcos verticales.

**Prioridad visual:** piso, espada, primer brasero, máscara, anticipación del custodio, arco de salida.

### Cripta de las Ascuas — Cautiverio

**Estado existente:** 4 salas, nichos con cráneos, ataúdes, cadenas, velas, acólitos, proyectiles, plataformas y Máscara de Ascua.

**Dirección [Propuesta]:** espacio comprimido y capas más densas, pero con suficiente lectura del primer plano. Volúmenes fríos y una presencia más inquietante de pequeños focos cálidos. Cadenas, nichos y ceniza evocan la retención de almas sin requerir efectos excesivos.

**Motivos:** triángulo, brasas, cadenas, incensarios, lápidas como coberturas.

**Prioridad visual:** línea y trayectoria del proyectil, cobertura reconocible, huecos y plataformas, recogida de maza y de máscara.

**Problema conocido:** el fondo lejano es demasiado oscuro según docs/etapa5/README.md; revisar los valores sin destruir la penumbra.

### Capilla del Último Sello — Autoridad

**Estado existente:** 3 salas, mármol, columnas, vitrales apagados, atril, estatuas, altar, custodio sellado y arena del Abad.

**Dirección [Propuesta]:** monumentalidad, más simetría y espacios de respiración visual. La arquitectura debe enmarcar al Abad y enfatizar su sello. El jugador llega de un mundo cargado de objetos a una composición más ritual, silenciosa y austera.

**Motivos:** sello circular o tallado, verticales monumentales, altar, guadaña, incensario.

**Prioridad visual:** diferencia entre tajo y lluvia, marcas de brasa en el suelo, sello vulnerable, cambios de fase y salida final.

### Transición emocional

Atrio: **promesa quebrada** → Cripta: **costo del juramento** → Capilla: **ruptura del sello** → Epílogo: **amanecer y descanso**.

Este recorrido visual interpreta la historia implementada; no agrega eventos canónicos.

## 7. Personajes, enemigos y lenguaje de siluetas

### Baldwin

**Rol:** protagonista y eje de escala. La hoja actual incluye Idle, Walk, Jump, Attack, Hurt y Dead en Sprites/Characters/Baldwin/. Las celdas son de 128 × 128; la documentación de etapa 5 sitúa el pie cerca de la fila 127 y el eje del cuerpo en columna 32. El personaje se orienta en un sentido y Godot lo voltea.

**Objetivo [Propuesta]:**
- Debe distinguirse del fondo incluso en el Atrio más oscuro.
- Su arma y la intención corporal deben destacar antes que ornamentos de armadura.
- Mantener pivote y posición de pie idénticos entre cuadros; evitar temblores entre animaciones.
- Refinar la caminata rígida y los cuadros de caída/deceso identificados en docs/etapa5/README.md.
- No cambiar colisiones ni timings mediante un rediseño meramente estético sin validación de gameplay.

### Custodio

**Rol:** primera gramática de ataque enemigo. Hoja actual de 4 poses, celda de 96 × 48 en el Atrio; el kit Meshy genera un cuerpo estático y compone la pose por inclinación y arma dibujada.

**Siluetas por fase [Base]:**
1. Reposo: arma baja.
2. Anticipación: arma arriba, ojos encendidos, aviso y punta brillante.
3. Ataque: arma horizontal que corresponde a la zona activa.
4. Recuperación: postura encorvada y arma baja o clavada.

**Propuesta:** añadir cuadros intermedios a mano o con una animación rigurosamente validada. Evitar la ilusión de que un modelo estático inclinado constituye animación completa de cuerpo.

### Acólito

**Rol:** enseñar ataques a distancia y cobertura. Su incensario sube durante la anticipación; después envía una brasa de trayectoria horizontal. Debe tener una silueta diferente a la del custodio por postura, objeto y ritmo.

### Custodio sellado

**Rol:** variante reforzada; no basta recolorear el custodio. **[Propuesta]** integrar una marca de sello y contraste de armadura reconocibles también sin color, sin alterar sus colisiones o timings por accidente.

### Abad Sellado

**Rol:** clímax visual y mecánico. Hoja actual de 9 cuadros de 224 × 128.

**Contrato de legibilidad:**
- Tajo: guadaña hacia atrás, línea baja de acción y espacio de salto.
- Lluvia: incensario alto, marcas inequívocas en suelo con huecos seguros.
- Vulnerabilidad: sello del pecho luminoso **y pose diferente**.
- Fase 2: intensificar el ritmo, nunca sustituir señales por ruido o flashes.

**Pendiente existente:** revisar especialmente cuadros 2 y 8 del Abad. En la arena, reducir decoración del plano jugable para que sus patrones dominen la composición.

## 8. Máscaras, armas y objetos

### Máscara del Voto

**Significado:** protección, juramento y peso del deber.  
**Código visual [Base]:** óvalo, marfil y materiales fríos.  
**Propuesta:** superficie envejecida y simetría casi ceremonial. La forma debe mantenerse reconocible en HUD, pickup y arte narrativo.

### Máscara de Ascua

**Significado:** riesgo, fuerza y fuego aún activo.  
**Código visual [Base]:** triángulo con cobre/brasa. El sprite actual del kit Meshy emplea acero oscuro con ojos de brasa.  
**Propuesta:** silueta angulosa claramente distinta del Voto; no depender sólo del naranja para identificarla.

### Armas

- **Espada de Baldwin:** arma inicial; lectura horizontal/larga y golpe rápido.
- **Maza de la Cripta:** diferenciación visual clara por peso, cabeza y golpe más contundente. No equiparar automáticamente sus valores a la maza de laboratorio.
- **Maza de prueba:** asset funcional pero no referencia de arte final para la campaña.

### Objetos del mundo

- Pickups sobre pedestales con brillo corto y aviso [R].
- Brasero: apagado (ceniza) frente a encendido (llama clara y volumen visual mayor).
- Arco de salida: luz de brasa **más** chevrones y estandartes.
- Foso: oscuridad, geometría inequívoca y púas visibles.
- Lápida: elemento de mundo; en Cripta debe ser inmediatamente claro cuándo actúa como cobertura real.

**Propuesta:** no introducir resplandores permanentes a todas las urnas y velas. Reservarlos para diferenciar estados interactivos.

## 9. Animación, VFX y accesibilidad

### Principios

- Mantener la correspondencia **anticipación → activo → recuperación** con las ventanas de scripts y recursos.
- Una animación nunca debe comunicar un hitbox antes o después de su ventana real.
- Combinar forma, postura y texto/indicador; el sonido es un canal adicional.
- Conservar una ruta de lectura segura en modo de efectos reducidos.

### Parámetros actualmente documentados [Base]

- Cambio de sala: fundido negro de 0,25 s.
- Hit flash / invulnerabilidad del jugador: hasta 0,6 s; no más de 3 parpadeos por segundo según la guía original.
- VFX de impacto futuros: idealmente no más de 0,3 s y nunca sobre el área crucial del golpe.
- La opción de efectos reducidos suaviza destellos y elimina parpadeo en marcas de brasa del jefe.
- La etapa 4 no utiliza luces 2D dinámicas; el brillo se incorpora a los sprites.

### VFX futuros [Propuesta, no implementados]

| Efecto | Intención | Restricción |
| --- | --- | --- |
| Ceniza suspendida | Ambiente de Cripta | Baja densidad; detrás de acciones |
| Polvo de pisada | Peso del movimiento | No cubrir los bordes del suelo |
| Estela de filo | Dirección del ataque | Seguir hitbox real y ventana activa |
| Pulsación del sello | Vulnerabilidad del Abad | No sustituir su pose informativa |
| Fuego del brasero | Estado de checkpoint | Diferencia visible apagado/encendido |
| Iluminación del amanecer | Resolución emocional | Reservada para el final narrativo |

Ninguna fila significa que el efecto ya exista en el código.

## 10. UI, HUD y tipografía

**Base:** Themes/baldwin_ui.tres, tipografía marfil con borde oscuro de 3 px, salud arriba a la izquierda, inventario de armas y máscara abajo a la izquierda. La ranura de intercambio usa el borde de brasa y el HUD muestra nombre, efecto y cooldown de máscara. Menús con foco de brasa y navegación por teclado.

**Propuestas para el acabado:**
- Priorizar un sistema tipográfico pixel compatible con «á é í ó ú ü ñ ¿ ¡ « » —»; confirmar licencia y render en Godot.
- Mantener una familia consistente de bordes: línea de acero, acento de brasa sólo en estados activos.
- Dar máxima prioridad a salud y eventos de combate, y menor peso a decoraciones de panel.
- Mostrar iconos de máscaras con su silueta propia; incorporar texto para distinguir efecto.
- Diseñar pantalla de título y menús como prolongación de la arquitectura funeraria, sin sacrificar legibilidad.
- Sustituir icon.svg estándar de Godot por un icono propio de sello/brasero/escudo —concepto a aprobar— antes de lanzar.

### Prueba de UI

Capturar a 640×360, ×2 y ×3; comprobar glifos, foco de teclado, contraste, textos largos, superposición con barra del jefe y efectos reducidos. El estado visual no queda validado sólo por pruebas headless.

## 11. Audio como parte de la dirección artística

### Lenguaje sonoro [Base]

- Bus **Music:** ambientes de sala y música del jefe; la fuente de sonido cambia con fundido.
- Bus **SFX:** ataque, impacto, recogida, máscara, checkpoint, lanzamientos y señales del Abad.
- Bucle de ambiente de aproximadamente 8 segundos en los assets generados.
- Cuando una sala continúa con el mismo ambiente, la reproducción no se reinicia; al cambiar, el sistema lo funde.
- El acólito y el jefe tienen señales sonoras diferentes por patrón.

### Intención [Propuesta]

El Atrio debe sonar vacío y pétreo; la Cripta, opresiva y cargada de resonancia; la Capilla, solemne y de gran volumen acústico. Sonidos metálicos, campanas apagadas, ceniza e incensario pueden funcionar como motivos sin copiar grabaciones ajenas.

**Regla:** nunca dejar que el sonido sea el único indicador de una amenaza. La mezcla debe permitir percibir anticipaciones y golpes por encima del ambiente.

**Estado real:** los bucles y efectos actuales fueron sintetizados por código y los informes mencionan validación técnica de picos/duración, pero no una auditoría a oído en altavoces reales. Tratar la mezcla como provisional.

## 12. Pipeline actual: Godot + generación programática + Meshy

### A. Generadores de prototipo [Base]

- tools/gen_atrio_assets.py: sprites y audio de referencia para el Atrio.
- tools/gen_zone_assets.py: sprites de Cripta/Capilla, Baldwin, jefe, intro, epílogo y sonidos.
- docs/etapa5/assets_manifest.md: dimensiones, cuadros, pivotes y archivos generados.

**Riesgo:** un generador que sobrescribe un sprite retocado puede destruir trabajo artesanal. Mantener una copia fuente y documentar el orden de generación.

### B. Kit 3D de Meshy [Base]

Art/Meshy/ contiene registros y previews de **10 conceptos**: lápida, custodio, urna, pedestal, candelabro, máscara del Voto, arco de salida, estandarte, máscara de Ascua y brasero. Hay renders, sprites derivados y registros de tareas. El README de procedencias reporta trabajo de generación con Meshy el 17 de noviembre de 2026.

**Precisión importante:** aunque el manifiesto registra glb=true, los ficheros .glb no están visibles en el árbol versionado revisado. Conservar los originales fuera de Git si pesan demasiado y documentar ubicación y posibilidad de recuperación.

### C. Conversión a sprites [Base]

tools/meshy_to_sprites.py:
1. Lee Art/Meshy/renders/*.png.
2. Recorta a la silueta útil.
3. Reduce al canvas previsto, apoyando en el borde inferior.
4. Cuantiza a los colores de la guía y tonos intermedios, sin dithering.
5. Agrega borde claro de acero o marfil.
6. Guarda en Art/Meshy/sprites/.
7. Con --install sustituye sprites homónimos en Sprites/.

El kit incluye casos especiales: arco con interior de brasa y chevrones, brasero de 4 cuadros, estandarte con indicación de salida y custodio compuesto por cuerpo y líneas de arma. Esas transformaciones no son equivalentes a una animación 3D riggeada.

### D. Pipeline recomendado para assets nuevos [Propuesta]

**Brief → siluetas → fuente 2D/3D → render controlado → pixelización → corrección manual → prueba en contexto → revisión de licencias → integración.**

| Etapa | Criterio de aceptación |
| --- | --- |
| Brief | Zona, función, dimensiones, pivote, paleta y niveles de importancia definidos |
| Silueta | Se entiende en negro sólido y a escala final |
| Fuente | Nombre de autor/herramienta, derechos y versiones registrados |
| Conversión | Fondo transparente, proporciones y tonos compatibles con guía |
| Corrección | Bordes sin ruido, clusters consistentes, lectura de forma |
| Animación | Pivote estable; fase/pose coincide con ventanas reales |
| Integración | Sin mismatch con colisión, z-index ni HUD |
| QA visual | 640×360, ×2, ×3, grises y efectos reducidos |
| Publicación | Derechos de distribución y créditos resueltos |

**No convertir todo el juego a 3D por tener Meshy.** El estilo objetivo sigue siendo 2D pixel art; el 3D puede ser un paso de generación, no el lenguaje gráfico final.

### E. Convenciones para cambios nuevos [Propuesta]

- Sprites instalados: Sprites/<categoria>/<zona_o_personaje>/<nombre>.png.
- Fuentes editables: Art/Source/<categoria>/<nombre>/ (si se decide introducir esta carpeta).
- Renders y previews: Art/Meshy/ para assets derivados de Meshy.
- Registro por asset: nombre, autor, fuente, licencia, zona, dimensiones, cuadros, pivote, método de generación, responsable y fecha.
- Todo cambio de tamaño de hoja o pivote requiere revisar escenas y docs/etapa5/assets_manifest.md.
- Nunca modificar arte de gameplay sin contrastarlo con las ventanas de daño y las colisiones.

## 13. Estándares de calidad y checklist

### Entrega de un sprite

- [ ] La silueta se reconoce a tamaño real.
- [ ] Respeta la paleta o justifica tonos adicionales.
- [ ] Mantiene la cuadrícula y nearest-neighbor.
- [ ] Tiene transparencia correcta, sin halos extraños.
- [ ] Pivote y pies permanecen estables.
- [ ] Las poses corresponden al comportamiento real.
- [ ] Ningún pixel ornamental oculta información jugable.
- [ ] Se ve bien sobre fondos oscuros y en grises.
- [ ] Sus derechos, créditos y fuente están documentados.
- [ ] Fue inspeccionado dentro de una escena Godot real.

### Revisión de una sala

- [ ] Se distingue el suelo colisionable del vacío.
- [ ] La posición del jugador es clara junto al fondo.
- [ ] Anticipaciones enemigas son visibles a ambos lados.
- [ ] Pickups, checkpoint y arco de salida tienen formas distintas.
- [ ] Los efectos no cubren obstáculos ni marcas del jefe.
- [ ] Los planos de parallax aportan profundidad sin distraer.
- [ ] La composición sigue funcionando durante el movimiento.
- [ ] Se revisaron escala 1× / 2× / 3× y escala de grises.

### QA de audio/UI

- [ ] Se entienden amenazas sin sonido.
- [ ] La mezcla no tapa SFX de anticipación.
- [ ] Los bucles no producen saltos perceptibles.
- [ ] El foco de menú se ve con claridad.
- [ ] El modo de efectos reducidos mantiene señales jugables.
- [ ] Los textos españoles y el HUD se leen a 640×360.

## 14. Backlog artístico priorizado

| Prioridad | Tarea | Por qué |
| --- | --- | --- |
| Alta | Auditoría de licencias de assets antiguos, shader y kit Meshy | Imprescindible antes de distribuir |
| Alta | Comprobar custodia y recuperación de modelos/renders fuente | Reproducibilidad del pipeline |
| Alta | Refinar cuadros críticos del Abad y del custodio | Señales de combate consistentes |
| Alta | Playtest visual del jefe, proyectiles y cobertura | Legibilidad real del gameplay |
| Media | Ajustar fondo lejano de Cripta | Problema identificado en etapa 5 |
| Media | Refinar Walk y Dead de Baldwin | Cohesión y calidad de animación |
| Media | Revisión a oído y mezcla final de ambiente/SFX | Audio provisional |
| Media | Diseñar icono propio y evaluar tipografía pixel | Identidad de publicación |
| Media | Revisar todas las capturas en 1×/2×/3× y grises | Control de presentación |
| Baja | Introducir VFX mínimos de ceniza/impacto | Atmósfera sin perder claridad |
| Baja | Ampliar variantes de utilería | Sólo si se preserva el contraste |

## 15. Decisiones abiertas de arte

1. **¿Qué acabado se aprueba?** Pixel art estrictamente dibujado a mano, híbrido con renders 3D convertidos o mezcla controlada por categoría.
2. **¿Qué elementos de Meshy entran definitivamente al juego?** Confirmar cómo se integran sin perder coherencia con Baldwin, jefe y zonas.
3. **¿Cuál será la fuente tipográfica final?** Legibilidad, glifos españoles y licencia.
4. **¿Qué nivel de animación final se exige a custodios y Abad?** Cuadros clave mínimos frente a animación intermedia pulida.
5. **¿Qué simbolismo principal tendrá el logotipo?** Sello, voto, brasa o una combinación original.
6. **¿Quién aprueba cambios de paleta, silueta, UI y sonido?** Establecer un responsable y revisión en pull request.

Ninguna de estas decisiones debe asumirse como aprobada por existir en este documento.

## 16. Referencias internas y jerarquía

- [Contexto integral](CONTEXTO_PROYECTO.md) — historia, sistemas, estado y riesgos.
- [Guía original de arte](arte.md) — paleta y restricciones técnicas que ya regían la sala de referencia.
- [Inventario y derechos](assets.md) — autoría, procedencias y permisos.
- [Informe de la sala de referencia](etapa4/README.md) — capturas 1×, ×2, ×3, grises y grabación.
- [Informe de la campaña](etapa5/README.md) — problemas de arte y playtests aún pendientes.
- [Manifiesto de imágenes/audio](etapa5/assets_manifest.md) — tamaños, cuadros y pivotes.
- [Menús y accesibilidad](etapa6/README.md) — controles, ajustes, capturas y estado real.
- tools/meshy_to_sprites.py — transformación 3D → sprite; tools/gen_atrio_assets.py y tools/gen_zone_assets.py — generación actual.

---

**Principio de cierre:** una buena imagen de Baldwin's Curse no sólo parece gótica. Hace inequívoco el siguiente salto, el siguiente golpe, el peligro y el último sello. El arte guía la acción y, al mismo tiempo, cuenta la tragedia de la abadía.
