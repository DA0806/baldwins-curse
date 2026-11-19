# Sprites prerenderizados de Baldwin's Curse

> La pasada actual de animación y equipo independiente se documenta en [animation_v2/README.md](animation_v2/README.md). Los conteos y comandos de esta primera pasada se conservan como registro histórico.

Fecha: 17 de noviembre de 2026. Estado: lote integrado de 10 hojas y 52 cuadros; cuatro modelos Meshy con rigs y animación base de Baldwin. Verificación técnica y capturas del juego completadas; partida humana pendiente. Esta guía conserva el combate y los contratos de las escenas. Complementa [arte.md](arte.md) y [DIRECCION_ARTISTICA.md](DIRECCION_ARTISTICA.md).

## Intención visual

Producir sprites 2D a partir de modelos y renders 3D, con volumen de tela, malla y metal legible a 640×360. Mantener vista lateral, escala entera, filtro nearest y el contraste de la abadía funeraria: piedra fría, acero, marfil, cobre envejecido y brasa para información activa. El material prerenderizado debe integrarse en el mundo existente sin cambiar hitboxes, alcances, ventanas de daño ni velocidad de juego.

Baldwin se distingue por su túnica marfil y equipo de guerrero; los custodios, por sus masas oscuras; el acólito, por capucha e incensario; el Abad, por altura, guadaña y sello. Reducir el detalle que se convierta en ruido al tamaño final. Mantener siluetas distintas durante anticipación, golpe y recuperación, también en grises.

## Referencia histórica y ficción

El canon del juego presenta a Baldwin como antiguo guardián de una abadía. La inspiración en **Balduino IV de Jerusalén** orienta el vestuario y la dignidad del personaje; no convierte el argumento en una biografía ni identifica al Abad o a los enemigos con personas históricas.

Guillermo de Tiro describe al joven Balduino como atractivo para su edad, hábil con caballos y afectado por una enfermedad progresiva. Ese texto no permite reconstruir sus facciones exactas. Los pasajes revisados no documentan una máscara de plata. Si el diseño incorpora máscara, debe registrarse como objeto ficticio del juego, con diseño propio; no presentarla como equipo histórico demostrado ni reproducir la utilería de una película. La enfermedad histórica tampoco establece el origen de la maldición fantástica. [Fuente 1](https://sourcebooks.fordham.edu/source/tyre-cde.asp)

La base material recomendada es malla con cofia, túnica o sobreveste sobria, cuero y espada recta de una mano. Evitar armadura completa de placas y hombreras enormes cuando se invoque el siglo XII como referencia: el Metropolitan Museum sitúa la armadura de placas de cuerpo entero hacia 1420. El color marfil y los acentos de cobre responden a la paleta del juego; no son una atribución documentada del vestuario personal del rey. [Fuente 2](https://www.metmuseum.org/es/essays/arms-and-armor-in-medieval-europe)

| Referencia | Qué aporta | Límite de uso |
| --- | --- | --- |
| [1. Guillermo de Tiro, selección traducida, Fordham](https://sourcebooks.fordham.edu/source/tyre-cde.asp) | Testimonio contemporáneo sobre juventud, carácter y enfermedad de Balduino IV | No es un retrato facial ni un catálogo de su equipo |
| [2. Arms and Armor in Medieval Europe, The Met](https://www.metmuseum.org/es/essays/arms-and-armor-in-medieval-europe) | Evolución de malla, cascos y placas | Referencia de época, no posesiones personales de Balduino |
| [3. Espada 07.53.2, The Met](https://www.metmuseum.org/art/collection/search/25601) | Hierro, proporciones y espada occidental; datación posiblemente XII–principios del XIII | Mantener la incertidumbre de fecha; imagen marcada como dominio público |
| [4. Pomo 2015.696, The Met](https://www.metmuseum.org/art/collection/search/665677) | Disco de aleación de cobre y esmalte, siglos XII–XIII | No atribuir su heráldica al protagonista; imagen marcada como dominio público |
| [5. Histoire d'Outre Mer, Walters W.137](https://api-dev.thedigitalwalters.org/Data/WaltersManuscripts/html/W137/description.html) | Coronación de Balduino IV en folio 252r; lenguaje iconográfico medieval | Manuscrito de finales del XIII, posterior al rey; no retrato del natural |

Los custodios pueden usar materiales de esa tradición. Sellos, ojos de brasa, guadaña del Abad y efectos sobrenaturales siguen siendo decisiones de ficción. La forma de cada arma debe responder a su función de combate.

## Contratos de integración

Todas las hojas son tiras horizontales RGBA, miran a la derecha y se voltean en el motor. Las coordenadas siguientes son de celda, con origen arriba a la izquierda e índices desde cero. Un apoyo en la última fila opaca queda un píxel por encima del borde geométrico de colisión.

| Actor | Celda y cuadros | Origen de celda que representa la raíz | Apoyo y colisión |
| --- | --- | --- | --- |
| Baldwin | 128×128; Idle 4, Walk 8, Jump 6, Attack 5, Dead 6, Hurt 2 | `(32,96)` con sprite centrado y offset `(32,−32)` | Eje x32, pies y127; cuerpo erguido de unos 64 px; colisión 24×64 centrada |
| Custodio y custodio sellado | 96×48; 4 cuadros | `(48,24)`; Art sin offset ni escala | Pies y47; cuerpo de unos 48 px; colisión 24×48 |
| Acólito | 64×48; 4 cuadros | `(32,24)`; Art sin offset ni escala | Pies y47; cuerpo de unos 42 px, incensario más alto; colisión 20×48 |
| Abad | 224×128; 9 cuadros | `(112,64)`; Art sin offset ni escala | Apoyo del cuerpo y120; cuerpo erguido de unos 111 px; colisión 48×112 |

Estos tamaños visuales aproximados proceden del arte anterior y orientan la escala. El arma, la capa y los efectos pueden extenderse fuera de la caja del cuerpo. En el Abad, la caja alfa total también incluye astil, incensario y partículas: no usarla sola para alinear el suelo.

### Baldwin

`Scenes/player.tscn` usa AnimatedSprite2D. `Player.gd` conserva el eje del cuerpo al girar mediante `flip_h` y el cambio de offset horizontal de +32 a −32. No recentrar el PNG automáticamente en x64.

- Idle: cuatro cuadros a 2 fps; Walk: ocho a 7 fps; Jump: seis a 10 fps, sin bucle; Dead: seis a 10 fps, sin bucle.
- Attack: cinco cuadros; los primeros cuatro corresponden a preparación. El script ajusta la reproducción a la anticipación del arma y fuerza el último cuadro cuando abre la ventana activa. Ese último cuadro continúa durante la recuperación.
- Estela de espada de referencia: x38–92, y76–116, equivalente a local x6–60, y−20–20. Conservar la relación entre gesto y daño real. Una maza tiene menor alcance aunque reutilice esta animación.
- `Hurt.png` no está enlazado en la escena ni se reproduce. Es una hoja fuente; la reacción actual usa empuje, cancelación y modulación del sprite. Activarla requeriría otro cambio de comportamiento.

### Custodios

`GroundEnemy.gd` selecciona 0 reposo, 1 anticipación, 2 activo y 3 recuperación. No hay ciclo de caminata independiente. El `!` es un nodo aparte; Body, Eye y Blade provisionales se ocultan cuando existe Art.

La zona de golpe predeterminada ocupa local x6–42, y−16–16 mirando a la derecha: celda x54–90, y8–40. La pose 2 debe extender el arma sobre esa zona. La anticipación predeterminada es 0,5 s; el custodio sellado puede configurar otros valores en la sala. Conservar el sello como distinción de forma, además de color.

### Acólito

`RangedEnemy.gd` selecciona 0 reposo, 1 anticipación, 2 lanzamiento y 3 recuperación. La mano que origina el proyectil debe estar alrededor de **`(46,16)`** en la pose 2, equivalente al `spawn_offset=(14,−8)` local. El incensario alzado distingue la pose 1.

Los valores predeterminados son 0,6 s de anticipación, 0,15 s de lanzamiento y 0,7 s de recuperación. El proyectil es otro objeto; no incluir una brasa separada permanente en el cuerpo que sugiera una segunda trayectoria.

### Abad Sellado

| Cuadro | Estado | Señal necesaria |
| --- | --- | --- |
| 0 | DORMANT / ADVANCE | Reposo, sello frío |
| 1 | SWEEP_TELL | Guadaña cargada hacia atrás, `!` externo |
| 2 | SWEEP | Barrido bajo, sello frío |
| 3 | SWEEP_RECOVER | Postura de recuperación y sello activo; vulnerable |
| 4 | RAIN_TELL | Incensario elevado; distinto de la guadaña atrás |
| 5 | RAIN | Acción de incensario/lluvia; sello frío |
| 6 | EXHAUSTED | Agotado y sello activo; vulnerable |
| 7 | STAGGER | Cambio de fase, sello partido; invulnerable |
| 8 | DEAD | Desplome, sello apagado o roto |

El barrido real parte del nodo MeleeAttack en y 44 y ocupa local x0–104, y32–56: celda **x112–216, y96–120**. Su anticipación base es 0,8 s y su activo 0,15 s; la lluvia anticipa 0,9 s. En fase 2 las anticipaciones duran 75 % del tiempo base. El arte no debe adelantar el golpe ni ocultar los huecos seguros de las marcas del suelo.

La recuperación del tajo dura 1,3 s y el agotamiento tras lluvia 1,6 s. La pose 7 puede ser luminosa, pero debe distinguirse de las ventanas vulnerables 3/6 por postura y forma del sello. Art sustituye Body, Seal, Scythe y Censer provisionales: esas señales deben existir dentro del render.

## Procedencia y uso real de Meshy

Un concepto, una miniatura del servicio y un modelo renderizado son entregables diferentes. Para llamar a un sprite **prerenderizado desde Meshy**, conservar el identificador de tarea, los parámetros de generación, el modelo descargado, la receta de cámara/iluminación/poses y la hoja final derivada. No describir inclinaciones o deformaciones de una imagen estática como animación esquelética.

El repositorio contiene conceptos, renders y metadatos de un kit Meshy anterior. La existencia de un registro con `glb=true` no demuestra que el archivo del modelo esté presente. Mantener fuentes pesadas fuera de Git cuando lo exija su tamaño y documentar una ubicación recuperable. No guardar enlaces de descarga temporales como única fuente ni incluir credenciales.

### Lote del 17 de noviembre

Se generaron cuatro referencias y cuatro modelos con geometría **Meshy t2.5**, textura **Meshy n1** y objetivo de **12 000 polígonos por modelo**; ese objetivo no equivale a un recuento medido de triángulos. Los prompts y los IDs de referencia/modelo están en `Art/Meshy/prerendered/manifest.json`. Los cuatro rigs tienen estado `SUCCEEDED`, registrado en `rigs/<personaje>/meta.json`.

| Personaje | Referencia | Modelo | Rig |
| --- | --- | --- | --- |
| Baldwin | `01a1ea0e-77b2-7143-8cb7-1060260df22e` | `01a1ea0f-6a00-7173-b605-ab44f7504dc2` | `01a1ea11-15ca-73a2-af79-60f61fbbef41` |
| Custodio | `01a1ea0e-7ccd-70eb-84f5-8b101db0e5b2` | `01a1ea0f-72e9-70da-8a1a-c58063d33921` | `01a1ea11-270e-7177-987d-df5e87be7756` |
| Acólito | `01a1ea0e-80d7-7271-ba07-174b70c92572` | `01a1ea0f-7d39-73e1-be07-d70c1ac0fae5` | `01a1ea11-37dd-719d-8345-742abf1e7d81` |
| Abad | `01a1ea0e-8578-7477-a2a9-bc1f528fae31` | `01a1ea0f-85f5-7492-ad91-236642dc1b07` | `01a1ea11-4c1c-70cd-8a1f-126f46126a02` |

El custodio sellado deriva del mismo modelo y rig del custodio, con sello y ataduras de geometría local; no es una quinta generación Meshy. Baldwin utiliza el caminar incluido con el rig y cuatro clips de la tarea de animación `01a1ea12-4115-739f-8ed8-896f4bddc7df`: **0 Idle**, **466 RegularJump**, **189 DyingBackwards** y **219 RightHandSwordSlash**. Los resultados están en `rigs/baldwin/actions/meta.json`; las acciones importadas se muestrean para las cantidades de cuadros del juego.

El consumo registrado del lote es **128 créditos Meshy**: 36 de referencias + 60 de modelos + 20 de rigging + 12 de clips. Son créditos del servicio, no una cotización en dinero ni una declaración de derechos de distribución.

Los cuatro modelos fuente descargados están en `Art/Meshy/prerendered/models/`. Sus huellas verificadas son:

| Modelo | SHA-256 |
| --- | --- |
| `baldwin.glb` | `7248ea85426746a2c882a63e3407724663e5913e2e87928df5751251ab967ab7` |
| `custodio.glb` | `3bea8656e1b9c1de5438edd4b125e0e3d3392feb177dc7394e5db30ccf7607fb` |
| `acolito.glb` | `347381216dbe87bee39b93adfe2c17ec4a92f2d28e3dc55730678ee6361e4924` |
| `abad.glb` | `148330d7ab73e00d9ba1d5f4734cfbeabc59bcbad4c07e5648b821ebe13a8f2b` |

### Render y conversión

`tools/render_characters.py` usa **Blender 4.5.9**, EEVEE, cámara ortográfica sin inclinación vertical, fondo transparente y renders RGBA a 4× la celda final. Conserva el encuadre por actor, retira el desplazamiento horizontal de locomoción de los clips y alinea el modelo al suelo antes de añadir equipo. La altura objetivo de render es 64 px para Baldwin, 44 para custodios, 41 para acólito y 108 para el Abad. Ilumina con luz principal marfil, borde de acero y relleno frío; la luz de señal se integra en el material, sin bloom.

La animación procede de huesos del rig: Baldwin muestrea los clips descargados; las poses adicionales de enemigos, Abad y Hurt se construyen con transformaciones de huesos e IK de brazos. Espadas, guadaña, incensario, sellos y ataduras se modelan localmente y se colocan en coordenadas de cámara. No se describen esas poses como nuevos clips generados por Meshy. La posición de las manos y el equipo necesita inspección sobre el render final, además de la validación del rig.

Cada pasada guarda `render_<actor>.json`. La primera pasada produjo 52 cuadros; todavía requiere las correcciones de apoyo y recorte indicadas arriba. `tools/pack_prerendered.py` aplica alfa premultiplicado, una reducción LANCZOS y una paleta de **153 colores** derivados de la guía, sin dithering. El manifiesto de empaquetado registrará las huellas del lote que finalmente se revise e instale.

| Evidencia del lote nuevo | Estado |
| --- | --- |
| Referencias, modelos, rigs y clips de Baldwin | Terminados; IDs y metadatos locales registrados |
| Modelos fuente descargados y sus huellas SHA-256 | Verificados en la tabla anterior |
| Cámara, escala, iluminación, resolución y método | Implementados en `tools/render_characters.py`; pasada final en corrección |
| Manifiesto de hojas instaladas y huellas SHA-256 | Pendiente tras revisar e integrar el lote final |
| Derechos del plan/modelo y créditos de distribución | Pendiente de comprobar; no inferir permiso sólo por tener un archivo |

No ejecutar `gen_atrio_assets.py`, `gen_zone_assets.py` ni un generador legado que sobrescriba los PNG finales sin restaurar después el lote aprobado. El manifiesto de etapa 5 describe el origen anterior; registrar la procedencia nueva por separado y actualizar el inventario de assets cuando termine la integración.

## Empaquetado reproducible

`tools/pack_prerendered.py` requiere Pillow. Recibe renders **RGBA a 4× el tamaño de celda final**, ya encuadrados por la cámara: no recorta ni recentra cuadros. Los archivos deben llamarse `000.png`, `001.png`, etc., sin saltos ni PNG adicionales dentro de cada carpeta.

| Carpeta bajo `Art/Meshy/prerendered/frames/` | Tamaño de entrada por cuadro | Cantidad |
| --- | --- | --- |
| `baldwin/Idle/` | 512×512 | 4 |
| `baldwin/Walk/` | 512×512 | 8 |
| `baldwin/Jump/` | 512×512 | 6 |
| `baldwin/Attack/` | 512×512 | 5 |
| `baldwin/Dead/` | 512×512 | 6 |
| `baldwin/Hurt/` | 512×512 | 2 |
| `custodio/poses/` | 384×192 | 4 |
| `custodio_sellado/poses/` | 384×192 | 4 |
| `acolito/poses/` | 256×192 | 4 |
| `abad/poses/` | 896×512 | 9 |

Desde la raíz del juego, preparar la revisión:

```sh
python3 tools/pack_prerendered.py
```

La herramienta valida el lote completo antes de escribirlo. Rechaza tamaños, modos de imagen y cantidades incorrectos, cuadros vacíos y siluetas cortadas en los bordes. Se permite tocar el borde inferior para Baldwin y enemigos pequeños, cuyos pies usan la última fila; el Abad debe conservar margen después de su apoyo en y120. El criterio de borde usa el mismo umbral alfa que la conversión, para ignorar residuos casi transparentes.

Reduce una sola vez con LANCZOS en alfa premultiplicado (`RGBa` de Pillow), aplica alfa binario con umbral 110 y asigna una paleta fija de rampas derivadas de los colores de la guía, sin dithering. Las rampas conservan transiciones de volumen y el alfa premultiplicado evita contaminar el contorno con el color de los píxeles transparentes. Para ajustar el umbral, usar `--alpha-threshold N` (1–255).

La salida es:

- `Art/Meshy/prerendered/sprites/`: diez hojas listas para Godot, con las mismas rutas relativas que `Sprites/`.
- `Art/Meshy/prerendered/gallery.png`: todos los cuadros a 1× y 3× en color y a 3× en grises sobre damero oscuro.
- `Art/Meshy/prerendered/comparison.png`: comparación de reposo y poses clave antes/después, más la versión nueva en grises.
- `Art/Meshy/prerendered/pack_manifest.json`: parámetros de conversión, paleta, cajas alfa, conteos y SHA-256 de entradas y hojas finales. No sustituye el registro de generación Meshy ni la receta del render.

El comando anterior **no cambia `Sprites/`**. Después de revisar las hojas, instalar con:

```sh
python3 tools/pack_prerendered.py --install
```

`--install` guarda una copia de cada hoja original en `Art/Meshy/prerendered/before/` sólo si esa copia aún no existe; nunca reemplaza ese primer respaldo. Las comparaciones siguientes usan ese respaldo. Los originales deben estar disponibles al empaquetar por primera vez. Los parámetros `--project-root`, `--frames-dir` y `--output-dir` permiten otra ubicación; la herramienta rechaza una salida dentro de `Sprites/` que eluda `--install`.

Las pruebas aisladas del empaquetador se ejecutan con `python3 -m unittest tools/test_pack_prerendered.py`. Usan proyectos temporales para comprobar el anclaje, los contornos, la validación del lote y la conservación del respaldo, sin modificar los sprites del juego.

## Verificación y evidencia

1. Validar dimensiones, número y orden de cuadros, transparencia y ausencia de recortes. Comparar escala de cuerpo y alineación de apoyo; no centrar cada pose por su caja alfa total.
2. Inspeccionar hojas en color y grises a 1× y 3×, con guías de eje y suelo. Revisar continuidad de identidad, volumen, luz y material entre cuadros, sin saltos de encuadre.
3. Superponer colisiones y ataque en ambas orientaciones; comprobar mano/proyectil del acólito y barrido bajo del Abad. La luz o estela no debe indicar daño fuera de su ventana real.
4. Capturar Atrio2, Cripta3 y Capilla3 a 640×360 y escalas enteras. Verificar legibilidad contra fondos, apoyos, `!`, sello vulnerable y señales con efectos reducidos.
5. Ejecutar pruebas existentes stage4, stage5 y stage6 después de importar los recursos. Registrar versión de Godot, salida, estado de los archivos y momento de ejecución. Las pruebas funcionales no sustituyen la inspección visual ni una partida humana completa.

| Comprobación | Estado |
| --- | --- |
| Baseline antes de sustituir sprites | Godot 4.7.2: stage4 18/18, stage5 45/45, stage6 54/54; salida 0 y cero fallas en las tres ejecuciones. Logs locales en `/tmp/baldwin-prerender-baseline-20261117/`; no son evidencia del lote nuevo |
| Pruebas funcionales sobre el lote instalado | Godot 4.7.2: stage4 18/18, stage5 45/45, stage6 54/54; 117 comprobaciones, cero fallas. Logs en `Art/Meshy/prerendered/qa/` |
| Capturas del lote instalado y revisión visual | Once escenas/estados en `docs/prerendered/capturas/`; galería 1×/3× y grises en `Art/Meshy/prerendered/gallery.png`, revisión independiente y corrección de agarre, barrido bajo y apoyo |
| Partida humana de la campaña y revisión de animación en movimiento | Pendiente |

## Regenerar los renders

Las fuentes GLB que necesita el render están versionadas en `Art/Meshy/prerendered/rigs/`: cuatro personajes articulados, la caminata incluida de Baldwin y su archivo de cuatro acciones. Los modelos sin rig descargados también permanecen localmente en `models/`, pero no son necesarios para regenerar. Los identificadores y SHA-256 están en `manifest.json`. Los metadatos temporales con enlaces firmados, los renders intermedios y los respaldos locales se excluyen del repositorio.

Con Blender 4.5.9 y Pillow, desde la raíz del juego:

```sh
blender --background --python tools/render_characters.py -- --actor baldwin
blender --background --python tools/render_characters.py -- --actor custodio
blender --background --python tools/render_characters.py -- --actor custodio_sellado
blender --background --python tools/render_characters.py -- --actor acolito
blender --background --python tools/render_characters.py -- --actor abad
python3 tools/pack_prerendered.py --install
```

No vuelve a generar en Meshy ni consume créditos: utiliza los GLB ya guardados. La iluminación, la escala ortográfica, el equipo local y las poses están definidos en el renderer. El render a 4× se reduce una sola vez; el tamaño lógico del juego sigue siendo 640×360.

El cuerpo se apoya después de resolver la IK, trasladando conjuntamente rig y objetivos. La rasterización puede dejar el último píxel opaco a ±1 px del apoyo geométrico; no se recentra cada imagen. Las armas se fijan a la muñeca evaluada conservando el extremo de combate. El renderer rechaza equipo por debajo del suelo; el mínimo registrado del lote es 0,020 m. La mano del acólito al lanzar queda en aproximadamente (45,76;15,72), frente al origen de proyectil (46;16), sin mover la lógica de combate.

El Abad tiene diferentes posturas de anticipación, barrido, recuperación y agotamiento; el gancho del cuadro activo apunta hacia abajo, dentro de la banda de ataque. Su sello está encendido en cuadros3/6, acompañado de postura agachada. La muerte de Baldwin usa la acción corporal de Meshy y la espada cae al suelo en los últimos cuadros. `Hurt.png` continúa sin usarse en runtime.

Para capturar el lote sin escribir partidas del jugador:

```sh
godot --path . --fixed-fps 60 -s res://tools/capture_prerendered.gd
```

El script reutiliza el recorrido de captura de la etapa5, desactiva guardado y elimina el destello temporal de daño sólo durante las capturas, para mostrar el material original. Esto documenta estados preparados; no equivale a una partida humana completa.
