# Animación y equipo independiente

Lote integrado el 17 de noviembre de 2026. Conserva la abadía funeraria, 640×360 y las estadísticas de combate.

## Cambios

Baldwin tiene reposo8, andar16, correr16, salto10, daño6, muerte12 y Dash12cuadros. La espada reparte16cuadros entre preparación6, activo4 y recuperación6; la maza usa20(8/4/8) con carga de hombro y mayor peso. Se reproducen las fases a sus tiempos reales: añadir cuadros no alarga el daño. Reposo mantiene un ritmo contenido; andar/correr ajustan su cadencia a la velocidad usando el recorrido medido de los pies.

Los custodios tienen36cuadros cada uno, el acólito30 y el Abad88:306cuadros de cuerpo en total. Se retiró la hoja antigua `Attack.png` con espada incrustada y la escena inicial sólo conserva una vista previa de reposo; los clips actuales se cargan desde el contrato generado. Cuerpo y equipo son capas separadas que comparten pose y reloj. La familia, textura y orientación del arma quedan fijadas al aceptar el golpe. Cambiar inventario no transforma un ataque en curso. El arma de reposo es la del último ataque mientras siga en inventario; inicialmente, la primera disponible.

Se corrigieron las proporciones: Baldwin64px, custodios60, acólito56 y Abad88. Las colisiones y hurtboxes se ajustaron manteniendo el apoyo, raíz y ruta originales. Los sprites de mundo ya no reutilizan el icono64×64 a tamaño nativo: máscaras20×24, espada32×32, maza28×28 y poción16×20. El HUD conserva iconos64×64 con márgenes.

## Modelos y procedencia

Se generaron cinco props con Meshy: espada, maza, guadaña, incensario y poción. Fuentes, referencias, identificadores, costos y huellas están en `Art/Meshy/animation_v2/equipment/manifest.json`. Se reutilizaron los rigs de personajes y sus clips incluidos; no fue necesario regenerar personajes ni pagar clips adicionales. Gasto real:120créditos (45referencias+75modelos), dentro del presupuesto129. La maza de prueba reutiliza geometría con otro acabado.

Los modelos originales y las animaciones que necesita la receta están versionados. Las referencias históricas y la distinción entre BalduinoIV y la ficción del juego siguen en `docs/arte_prerenderizado.md`. Los materiales de los props son propios del proyecto, generados con Meshy; sus condiciones de uso corresponden a la cuenta conectada, sin resolver automáticamente las procedencias pendientes de assets anteriores.

## Dash y poción: preparados

`Sprites/Characters/Baldwin/Dash.png` y sus anclajes contienen12cuadros a60fps (0,20s). La pose baja el centro de gravedad, inclina el torso y lleva el arma hacia atrás sin atravesar el suelo. Se puede previsualizar con el componente de presentación; no se añadió entrada, desplazamiento, invulnerabilidad ni cooldown de dash.

La poción tiene GLB, icono y sprite del mundo. No se añadió consumo, cantidad, tecla, restauración de salud ni cambio de guardado. La integración de healing futura debe definir esas reglas; `Health.set_current()` actualmente tiene semántica de restauración de estado/invulnerabilidad y no debe asumirse como curación normal.

## Archivos y regeneración

- `tools/render_animation_v2.py`: cuerpo sin equipo desde rigs Meshy y metadatos de mano evaluada; cámara fija, imágenesRGBA a4×.
- `tools/pack_animation_v2.py`: reducción única con alfa premultiplicado y paleta; instala17hojas/306cuadros y genera `BaldwinPoseData.gd`/`EnemyPoseData.gd`. El Abad usa cuadrícula8×11(2048×1760) para no exceder el límite gráfico de una tira22528px.
- `tools/render_equipment_v2.py`: equipo independiente, pivotes e iconos/recogibles desde los cinco GLB.
- `tools/preview_animation_v2.py`: muestras animadas con equipo usando los mismos anclajes.
- `tools/capture_animation_v2.gd`: once estados de campaña, sin guardar partidas y con tintes de daño neutralizados para revisar el arte.

Desde la raíz del juego, con Blender4.5.9 y Pillow:

```sh
blender -b --python tools/render_animation_v2.py -- --actor baldwin
blender -b --python tools/render_animation_v2.py -- --actor custodio
blender -b --python tools/render_animation_v2.py -- --actor custodio_sellado
blender -b --python tools/render_animation_v2.py -- --actor acolito
blender -b --python tools/render_animation_v2.py -- --actor abad
python3 tools/pack_animation_v2.py
python3 tools/preview_animation_v2.py
godot --path . --fixed-fps 60 -s res://tools/capture_animation_v2.gd
```

Los generadores y empaquetadores de la pasada anterior son históricos: reinstalarlos sobrescribiría el arte nuevo. Esta receta utiliza fuentes locales y no vuelve a gastar créditos Meshy.

## Evidencia

Pruebas: etapa1 80/80, etapa2 62/62, etapa3 64/64, etapa4 19/19, etapa5 45/45, etapa6 54/54; presentación de jugador21/21 y enemigos24/24. Total369, cero fallas. Logs en `Art/Meshy/animation_v2/qa/`. Se revisaron poses, agarres, reflexión, apoyo, máscaras/armas en mundo y capturas de campaña. Las capturas preparadas y pruebas automáticas no sustituyen una partida humana completa.

Muestras: [espada](Sword.gif), [maza](Mace.gif), [dash](Dash.gif), [carrera](Run.gif), [reposo](Idle.gif). LosGIF son demostraciones aproximadas; su temporización está limitada por el formato y no controla el combate.
