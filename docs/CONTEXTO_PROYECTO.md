# Baldwin's Curse — Contexto integral del proyecto

> **Documento vivo / fuente de contexto.** Corte: 17 de noviembre de 2026. Basado en la rama main del repositorio DA0806/baldwins-curse, el README, los informes de etapas 4–6, los recursos y escenas del juego.  
> **Estado:** las etapas 0–6 del roadmap están implementadas en el repositorio; la etapa 7 (build 1.0, distribución y validación final) está pendiente.  
> **Convención:** **[Implementado]** = comportamiento/documento presente; **[Objetivo]** = meta declarada que no equivale a validación; **[Propuesta]** = recomendación abierta a aprobación; **[Pendiente]** = tarea o incertidumbre.

## 1. Identidad y visión del producto

**Título:** Baldwin's Curse.  
**Tipo:** videojuego de acción y plataformas 2D, de un jugador, con combates de lectura y respuesta.  
**Motor / lenguaje:** Godot 4.7.x Standard y GDScript; el proyecto se probó con Godot 4.7.2, sin C#.  
**Formato visual:** pixel art de abadía funeraria, 640 × 360 de resolución lógica, escalado entero.  
**Entrada actual:** teclado.  
**Plataforma de salida inicial:** Windows x64 **[Objetivo]**; el material del repositorio dice que se ha ejecutado en macOS Apple Silicon y aún debe validarse la exportación de Windows.

### Promesa al jugador

Encarnar a Baldwin, regresar a una abadía que conserva a sus muertos bajo un sello, aprender a moverse y luchar, elegir entre efectos de máscaras y atravesar tres zonas para derrotar al Abad Sellado. La dificultad debe venir de interpretar anticipaciones claras y dominar la respuesta, no de sorpresas imposibles de leer.

### Pilares de diseño

1. **Lectura antes que reflejo ciego.** Cada amenaza anuncia su comportamiento por forma, animación y —como refuerzo— sonido.
2. **Combate deliberado.** Cada arma tiene anticipación, ventana activa, recuperación y enfriamiento; no hay ataque automático por mantener la tecla.
3. **Elecciones compactas.** Dos ranuras de armas y máscaras con efectos pasivos permiten alterar el combate sin crear sistemas innecesariamente grandes.
4. **Reintento comprensible.** Los braseros son puntos de control; morir o caer restaura el último estado guardado.
5. **Atmósfera legible.** La abadía es oscura, pero el suelo, las salidas, los pickups y los peligros destacan sin depender sólo del color.

Estos pilares sintetizan las mecánicas y reglas que ya documenta el repositorio, no constituyen un anuncio comercial aprobado.

## 2. Mundo, historia y tono

### Premisa canónica [Implementado]

El texto de entrada en Scenes/Intro.tscn establece que Baldwin juró guardar la abadía de los muertos. El Abad selló las almas para obligarlas a servirle eternamente; Baldwin huyó y la maldición lo hizo regresar. Sólo romper el último sello lo liberará.

**Protagonista:** Baldwin, antiguo guardián vinculado a la abadía y a su juramento.  
**Antagonista:** el Abad Sellado, responsable de mantener las almas sometidas.  
**Conflicto:** deber frente a cautiverio; culpa, juramento y liberación.  
**Objetivo narrativo:** romper el último sello para que los custodios descansen y Baldwin pueda dejar atrás la maldición.

### Narrativa ambiental [Implementado]

Las tres inscripciones se distribuyen en Cripta 1, Capilla 1 y Capilla 2. Explican que los guardianes quedaron atados por su voto, que el Abad encerró cada alma bajo un sello y que el último sello lleva el nombre de Baldwin. La clase Scripts/Rooms/Inscription.gd muestra el texto al aproximarse; no interrumpe la acción.

El epílogo de Scenes/Ending.tscn confirma que el último sello se quiebra, las ascuas se extinguen, los custodios descansan y Baldwin observa el amanecer después de quitarse el yelmo. También presenta el tiempo de partida y los reintentos.

### Tono y límites narrativos [Propuesta]

Mantener un relato melancólico, solemne y de fantasía gótica contenida: misterio y tragedia por encima del horror explícito. Contar con arquitectura, símbolos, iluminación y pocas frases concisas. Evitar introducir nuevos personajes, giros de trama o finales alternativos como hechos establecidos sin una decisión de dirección.

## 3. Alcance de la campaña

El alcance de trabajo en docs/alcance-1.0.md describe un juego corto de 20–35 minutos en una primera partida **[Objetivo]**. La estimación posterior del informe de etapa 5 fue **8–15 minutos**, aún **sin playtests con personas**. Atravesar las salas sin detenerse puede tomar poco más de un minuto; la duración real necesita medición.

| Zona | Salas / IDs estables | Función | Enfrentamientos y recompensas |
| --- | --- | --- | --- |
| **Atrio del Voto** | atrio_1, atrio_2, atrio_3 | Enseña movimiento, salto, espada, recogida, combate y Máscara del Voto | Maniquí, custodio y dos guardianes; dos braseros |
| **Cripta de las Ascuas** | cripta_1, cripta_2, cripta_3, cripta_4 | Introduce Máscara de Ascua, Maza de la Cripta, plataformas, proyectiles y cobertura | Custodio, acólito, custodio más dos acólitos; dos braseros |
| **Capilla del Último Sello** | capilla_1, capilla_2, capilla_3 | Introduce custodio sellado, prepara reglas del jefe y culmina la campaña | Custodio sellado, brasero de antesala y Abad Sellado |

**Ruta fija [Implementado]:** introducción → 3 salas del Atrio → 4 de la Cripta → 3 de la Capilla → epílogo.  
**Puntos de control [Implementado]:** checkpoint_atrio_2, checkpoint_atrio_3, checkpoint_cripta_1, checkpoint_cripta_3 y checkpoint_capilla_2. Antes del primero se utiliza el inicio del Atrio 1.

**Importante:** docs/etapa4/README.md describe la sala de referencia Atrio 2 con Ascua en un pedestal, pero la etapa 5 cambió ese pickup por la **Máscara del Voto**. La Ascua pertenece ahora a Cripta 1; para decisiones actuales prevalecen las escenas de campaña y docs/etapa5/README.md.

Las escenas viven en Scenes/Rooms; la ruta contractual y sus puntos se explican en [docs/etapa5/ruta.md](etapa5/ruta.md).

## 4. Sistemas de juego existentes

### 4.1 Movimiento y cámara [Implementado]

- Movimiento lateral con aceleración, fricción y control aéreo.
- Salto de altura variable, caída más rápida, coyote time, jump buffer y corrección de esquinas.
- Referencia medida en la sala de laboratorio, a 60 ticks/s: salto largo ~76,9 px de altura y ~129 px de alcance horizontal; salto corto ~19,2 px.
- Coyote time ~0,117 s, buffer ~0,133 s y corrección comprobada de esquinas ~6 px en las pruebas descritas en el README.
- Reglas de geometría del recorrido: huecos de hasta 96 px, escalones de hasta 64 px, y cámara limitada a cada sala.

**Código:** Scripts/Player.gd, Scripts/camera_follow.gd, Scripts/Room.gd y Scripts/Rooms/BlockGeometry.gd. Algunos parámetros exportados de Player.gd no coinciden exactamente con magnitudes medidas porque el comportamiento también depende de física, entradas y configuración de la escena; para balancear, medir jugando y consultar las pruebas.

### 4.2 Inventario, armas y combate [Implementado]

- Dos ranuras de arma. Al recoger una nueva se ocupa primero el hueco libre; si ambas están llenas, se reemplaza la ranura de intercambio. El arma desplazada queda en el suelo.
- La ranura de intercambio es la del último ataque válido (o la primera inicialmente); el HUD señala cuál se reemplazará.
- Cada ataque fija su arma, dirección y daño al aceptarse. Tiene anticipación, ventana de daño, recuperación y cooldown. La ventana activa puede dañar a cada objetivo una vez; mantener la tecla no repite el golpe.
- Personaje: 100 de salud; 0,6 s de invulnerabilidad después de recibir daño. El golpe recibido interrumpe el ataque y provoca retroceso.

| Arma | ID de datos | Daño | Alcance | Anticipación / activo / recuperación | Cooldown |
| --- | --- | --- | --- | --- | --- |
| Espada inicial (Copper Sword / espada de Baldwin en arte actual) | copper_sword | 20 | 60 px | 0,16 / 0,08 / 0,16 s | 0,4 s |
| Maza de prueba (laboratorio) | test_mace | 35 | 44 px | 0,28 / 0,10 / 0,32 s | 0,8 s |
| Maza de la Cripta | crypt_mace | Ver recurso Items/Weapons/Crypt_Mace.tres | Ver recurso | Ver recurso | Ver recurso |

No confundir el ítem de prueba test_mace con la recompensa crypt_mace de la campaña.

**Código:** Scripts/PlayerInventory.gd, Scripts/Combat/Health.gd, Hitbox.gd, Hurtbox.gd, MeleeAttack.gd, Scripts/Classes/WeaponData.gd y Scripts/ItemCatalog.gd.

### 4.3 Máscaras [Implementado]

| Máscara | ID | Forma de lectura | Efecto |
| --- | --- | --- | --- |
| Máscara del Voto | mask_vow | Óvalo marfil | Daño entrante ×0,80 |
| Máscara de Ascua | mask_ember | Triángulo / brasa y cobre | Daño de arma ×1,25 |

- Sólo modifica estadísticas la máscara activa.
- Se cambian con C / V y hay 1 segundo de recarga tras un cambio real.
- Cinto de hasta tres máscaras; actualmente la campaña contiene dos tipos. Con el cinto lleno, la nueva sustituye a la activa y la anterior cae.
- El daño ofensivo se fija al comenzar el ataque; cambiar de máscara durante la animación no altera ese golpe.

**Datos:** Items/Masks/Mask_Vow.tres e Items/Masks/Mask_Ember.tres.

### 4.4 Enemigos y jefe [Implementado]

- **Custodio cuerpo a cuerpo:** patrulla, detecta y persigue, levanta el arma y anuncia su golpe; la implementación de referencia parte de 60 puntos de salud y 15 de daño.
- **Acólito de la Ascua:** avisa durante 0,6 s con el incensario antes de lanzar una brasa horizontal de 12 de daño; puede evitarse saltando o mediante cobertura.
- **Custodio sellado:** variante de mayor resistencia, daño y rapidez de preparación (por ejemplo, en Capilla 1: 90 de salud, ataque de 20 y anticipación de 0,4 s).
- **Abad Sellado:** jefe con 300 de salud y dos patrones:
  - **Tajo bajo:** anticipación 0,8 s, barrido de 104 px que se salta, seguido de 1,3 s de vulnerabilidad.
  - **Lluvia de ascuas:** anticipación 0,9 s, tres marcas con separación de 80 px; los huecos son seguros. Queda vulnerable 1,6 s.
  - **Fase 2** al 50 % de salud: anticipaciones ×0,75, dos tajos por lluvia y cinco brasas separadas 64 px.
  - Sólo admite daño cuando el sello del pecho indica una ventana vulnerable.

**Código:** Scripts/Enemies/, Scripts/Bosses/, Scenes/Enemies/ y Scenes/Bosses/.

### 4.5 Puntos de control y estado [Implementado]

- Caer o morir restaura la **última activación del brasero**: sala, aparición, salud, armas, máscaras y recogidas únicas asociadas al estado de ese momento.
- Los enemigos y los objetos transitorios reaparecen; las recogidas anteriores al checkpoint no se duplican, y las posteriores se pierden con el reintento.
- GameSession es el nombre del autoload configurado en project.godot; su script Scripts/GameSession.gd declara la clase RunSession.
- Identidad estable: room_id para salas, spawn_id para apariciones, unique_id para pickups, y el catálogo de IDs para objetos. No persistir nodos de Godot ni rutas de escena arbitrarias en el estado.
- Una partida iniciada desde el título se guarda; abrir una escena aislada con F6 o un smoke test no debe tocar el archivo real.

### 4.6 Menús, guardado y ajustes [Implementado]

- Menú de título con Continuar, Nueva partida, Ajustes, Controles, Créditos y Salir.
- Pausa en juego con Reanudar, Volver al último brasero, Ajustes, Controles y Volver al título.
- Navegación de teclado, foco resaltado con brasa y confirmación antes de sobrescribir la partida.
- Guardado en una sola ranura, user://savegame.json, esquema versionado (versión 1), temporal y copia .bak. Hay recuperación y mensajes para archivo faltante, corrupto, incompatible o sala desconocida.
- Ajustes independientes en user://settings.cfg: master, música/ambiente, SFX, pantalla completa y efectos reducidos.
- El HUD muestra salud, dos armas, ranura de intercambio, máscara activa y su recarga.
- Al terminar, el epílogo presenta tiempo y reintentos; el título reconoce que la partida fue completada.

**Código:** Scripts/Save/, Scripts/UI/, Scenes/UI/, Scripts/inventory_hud.gd y Themes/baldwin_ui.tres.

## 5. Controles actuales

| Entrada | Acción |
| --- | --- |
| ← / → | Mover |
| Espacio / ↑ | Saltar; duración de pulsación afecta la altura |
| R | Recoger o intercambiar el pickup más cercano |
| Z / X | Atacar con arma de ranura 1 / 2 |
| C / V | Máscara anterior / siguiente |
| Esc / P | Pausar, volver de menú cuando corresponda |
| Flechas + Intro o Espacio | Navegar y confirmar menús |
| F3 (debug) | Mostrar/ocultar hitboxes y hurtboxes |

La fuente de verdad de los controles es el InputMap de project.godot. No hay remapeo de teclas en el alcance actual.

## 6. Arquitectura y organización del repositorio

| Carpeta / archivo | Responsabilidad |
| --- | --- |
| project.godot | Configuración del motor, escena principal, display, InputMap, autoloads y tema |
| Scenes/Rooms/ | Diez salas de campaña con room_id, geometría, spawns y salidas |
| Scenes/world.tscn | Laboratorio separado; no es una sala de campaña |
| Scenes/Intro.tscn, Scenes/Ending.tscn | Apertura y desenlace |
| Scenes/UI/, Scenes/InventoryHUD.tscn | Pantallas de menú y HUD |
| Scripts/ | Movimiento, combate, estados, inventario, enemigos, encuentros y transición |
| Scripts/GameSession.gd | Estado central, navegación, checkpoints, tiempo, reintentos y guardado |
| Scripts/Save/ | Persistencia y preferencias |
| Scripts/Classes/, Items/ | Definiciones y recursos de armas/máscaras |
| Sprites/ | Arte jugable; incluidos Baldwin, enemigos, jefe, zonas y UI de ítems |
| Art/Meshy/ | Metadatos, previews, renders y conversión de un kit 3D a pixel art |
| Audio/ | Ambientes, música del jefe y efectos |
| Shaders/ | Shader de brillo de pickups, con procedencia aún por resolver |
| Themes/ | Tema UI |
| Tests/ | Pruebas automatizadas de etapas 1 a 6 |
| tools/ | Smoke, generación de assets, conversión Meshy y capturas |
| docs/ | Alcance, guía original de arte, inventario de procedencias e informes |

### Decisiones técnicas relevantes

- Resolución lógica 640 × 360; ventana de referencia 1280 × 720; nearest-neighbor y escala entera.
- Cuadrícula de 16 px; geometría visual y colisión alineadas.
- Parallax2D con planos 0,2 (lejano) y 0,5 (medio).
- El ambiente sonoro se mantiene si dos salas comparten pista y se funde cuando cambia.
- El plugin opcional addons/godot_ai/ 3.2.4 está en el repositorio para edición; jugar no requiere su servidor. Verificar que no se incluya en la distribución final.
- Se utilizan datos de IDs estables como contrato entre escenas, pickups y guardado. Cambiar un ID es una migración de contenido, no un cambio cosmético.

## 7. Dirección visual actual y pipeline de assets

La guía original [docs/arte.md](arte.md) fija la abadía funeraria, los colores fríos de piedra y acero, y los acentos cálidos reservados para información importante. La **dirección artística de trabajo extendida** está en [DIRECCION_ARTISTICA.md](DIRECCION_ARTISTICA.md); debe leerse junto a la guía original, no reemplazarla silenciosamente.

### Fuentes de arte y audio presentes

1. **Dibujo/síntesis programática:** tools/gen_atrio_assets.py y tools/gen_zone_assets.py generan sprites, ambientes y efectos propios para el prototipo.
2. **Meshy, kit del Atrio:** Art/Meshy/ contiene registros de diez elementos (lápida, custodio, urna, pedestal, candelabro, máscaras, arco, estandarte y brasero), más previews, renders y sprites convertidos.
3. **Conversión 3D → 2D:** tools/meshy_to_sprites.py recorta, reduce, cuantiza a paleta, aplica contorno y coloca resultados en Art/Meshy/sprites; con --install los copia a Sprites/.
4. **Trabajo manual pendiente:** refinamiento de animaciones, siluetas, mezcla de audio, tipografía propia y ajustes de readability.

**Precaución:** volver a ejecutar tools/gen_atrio_assets.py sobrescribe sprites instalados desde Meshy. Si se necesita reconstruir el kit, regenerar lo programático y después aplicar la conversión Meshy con --install o trabajar sobre ramas/artefactos separados. Los archivos GLB se mencionan en docs/assets.md pero **no aparecen versionados en el árbol Git inspeccionado**: confirmar dónde se guardan los originales antes de asumir que el repositorio contiene los modelos recuperables.

**Procedencias:** [docs/assets.md](assets.md) documenta assets sin autor o permiso confirmado (sprites antiguos Knight_1, antiguo icono Copper_Sword, shader ItemShineHighlight y el icono estándar de Godot). El kit Meshy tiene derechos de distribución sujetos a confirmar según el plan de la cuenta. No considerar resuelta la licencia por el hecho de que exista el archivo en Git.

## 8. Estado de desarrollo y evidencia

| Etapa | Entregable | Estado documentado |
| --- | --- | --- |
| 0 | Baseline, smoke, alcance e inventario de assets | Implementado |
| 1 | Movimiento, cámara, recogidas e inventario | Implementado; 62 pruebas OK según etapa 6 |
| 2 | Combate, salud, enemigos básicos | Implementado; 61 pruebas OK |
| 3 | Máscaras, checkpoints y estado por IDs | Implementado; 64 pruebas OK |
| 4 | Sala de referencia con arte/audio/transiciones | Implementado; 18 pruebas OK |
| 5 | Campaña de 10 salas, enemigos, jefe, historia y epílogo | Implementado; 45 pruebas OK |
| 6 | Menús, guardado, ajustes, pruebas de errores | Implementado; 54 pruebas OK |
| 7 | Exportación, build 1.0 y validación para entrega | Pendiente |

Los números anteriores son **resultados reportados en la documentación del repositorio**, no una ejecución nueva de las pruebas durante la preparación de este documento. El smoke, los tests headless y las capturas automatizadas tampoco equivalen a una partida humana completa.

### Comandos de referencia

- Instalar Godot 4.7.2 Standard, importar project.godot y ejecutar F5 para abrir el título.
- F6 sobre Scenes/world.tscn abre el laboratorio.
- Definir la variable de entorno GODOT con la ruta del ejecutable.
- Ejecutar tools/smoke.sh y tools/smoke.sh --self-test.
- Ejecutar cada Tests/stageN_tests.gd con Godot --headless --fixed-fps 60 --path . -s res://Tests/stageN_tests.gd (N = 1…6).
- Ejecutar tools/stage5_capture.gd y tools/stage6_capture.gd desde Godot con ventana para imágenes de inspección.

Archivos de evidencia: [etapa4/](etapa4/README.md), [etapa5/](etapa5/README.md), [etapa6/](etapa6/README.md).

## 9. Problemas, riesgos y deuda conocida

| Prioridad | Tema | Estado / motivo |
| --- | --- | --- |
| P0 antes de distribuir | Licencia de assets y shader | Autoría o permiso no confirmado en algunos archivos; revisar también el plan de Meshy |
| P0 antes de distribuir | Build Windows x64 | Exportar en máquina y probar arranque, pausa, audio, guardado, reanudación y cierre |
| P0 antes de distribuir | Excluir addon de desarrollo | Comprobar que godot_ai y su autoload de depuración no lleguen al paquete final |
| P1 | Playtests humanos | Duración, dificultad del jefe, curva de aprendizaje y lectura de señales no están medidas |
| P1 | Arte y animación | Caminar de Baldwin algo rígido, muerte con cuadros rotados, ciertos cuadros del Abad y fondo de Cripta |
| P1 | Audio | Bucles sintetizados verificados técnicamente pero aún sin revisión crítica a oído en altavoces |
| P1 | Arte Meshy | Revisar pivotes, consistencia con colisiones, poses inventadas sobre modelos estáticos y continuidad visual |
| P1 | Icono y tipografía | Sustituir icono Godot y considerar fuente pixel propia con glifos españoles |
| P2 | Alcance extra | Más máscaras, rutas opcionales, soporte de mando, combos, logros, web o soltar armas manualmente: fuera del 1.0 actual |

**Duración:** no expandir contenido automáticamente para perseguir 20–35 minutos. Primero medir partidas de personas y determinar si la experiencia corta funciona mejor o si hay que alargar encuentros/salas.

## 10. Ruta sugerida hacia 1.0 [Propuesta]

1. **Congelar el contrato:** revisar IDs, orden de salas, pickups y guardado; decidir qué partes del alcance son esenciales para cerrar la versión.
2. **Auditoría de arte y derechos:** resolver procedencias, identificar sprites finales frente a provisionales y congelar la paleta y las reglas de animación.
3. **Pase de legibilidad:** revisar en 640×360 y grises todas las anticipaciones, pickups, obstáculos y momentos del jefe; repetir en 2× y 3× en monitor real.
4. **Pase de audio:** auditar volumen, bucles, prioridad de SFX, lectura sin audio y opción de efectos reducidos.
5. **Playtesting:** observar partidas completas sin asistencia; registrar finalización, muertes por sala, confusiones, tiempos y accesibilidad.
6. **Corrección enfocada:** modificar sólo aquello que los tests y playtests justifiquen; mantener la ruta y guardado compatibles.
7. **Exportación Windows:** configurar preset, generar ejecutable, verificar exclusiones del addon y comprobar guardado después de cerrar y reabrir.
8. **Cierre:** versión, changelog, créditos, licencias, instrucciones de instalación y una build candidata probada.

### Criterio mínimo sugerido para considerar la 1.0 lista

- Campaña completa recorrida manualmente desde título hasta epílogo, sin errores bloqueantes.
- Guardar/cerrar/continuar probado en build exportada.
- Legibilidad del combate y del jefe confirmada con jugadores que no conocen los controles.
- Ningún asset distribuido con permisos pendientes.
- Audio y controles funcionales, incluidos los modos de efectos reducidos.
- Smoke y Tests/stage1…stage6 sin regresiones.
- Ejecutable Windows x64 revisado en un equipo real.

## 11. Convenciones para trabajar en adelante

**Fuente de verdad por responsabilidad:**
- Historia mostrada al jugador: Scenes/Intro.tscn, Scenes/Ending.tscn e inscripciones en Scenes/Rooms/.
- Mecánicas y números: recursos Items/, scripts Scripts/ y pruebas Tests/.
- Ruta / guardado: Scripts/GameSession.gd, docs/etapa5/ruta.md y Scripts/Save/.
- Arte aprobado: docs/arte.md y [DIRECCION_ARTISTICA.md](DIRECCION_ARTISTICA.md), más los assets que estén efectivamente instalados.
- Estado de entregas: README.md y docs/etapaN/README.md.
- Derechos: docs/assets.md.

**Reglas de cambio:** actualizar documentos junto con la implementación; no declarar “terminado” sólo por una captura; mantener los IDs estables o diseñar migración; registrar procedencia de assets; separar “hecho”, “validado” y “propuesto”.

### Decisiones abiertas para la dirección

- ¿El objetivo de experiencia final será 8–15 o 20–35 minutos, después de playtesting?
- ¿El pipeline Meshy → sprite será el estándar para todos los assets o sólo el Atrio?
- ¿Qué grado de redibujo manual se exigirá para la animación de personajes y jefe?
- ¿Qué se hará con los assets legados y el shader de procedencia incierta?
- ¿Qué plataformas y requisitos de equipo se anunciarán cuando la primera build sea verificable?

## 12. Lecturas y enlaces internos

- [README del repositorio](../README.md) — descripción y comandos.
- [Alcance de la 1.0](alcance-1.0.md) — intención original.
- [Guía de arte original](arte.md) — reglas de la sala de referencia.
- [Dirección artística ampliada](DIRECCION_ARTISTICA.md) — visión estética, pipeline y QA de arte.
- [Inventario de assets y permisos](assets.md) — procedencias.
- [Etapa 4](etapa4/README.md), [etapa 5](etapa5/README.md), [ruta](etapa5/ruta.md), [etapa 6](etapa6/README.md).
- [Manifiesto de sprites y audio](etapa5/assets_manifest.md).
- Repositorio: https://github.com/DA0806/baldwins-curse

---

**Mantenimiento del documento:** revisar al modificar gameplay, narrativa, arte aprobado, alcance o status de la build. El texto distingue condiciones observables en el repositorio de propuestas de trabajo; no debe convertirse en una lista de funcionalidades anunciadas sin verificación.
