# Etapa 6 · Menús, accesibilidad y guardado

Desde el arranque normal se puede empezar, pausar, reanudar, volver al último brasero, volver al título, cerrar el juego y continuar al reabrirlo. Todo se maneja con el teclado.

## Flujo

```text
Título ─ Continuar ───────────────► sala del último brasero
       ─ Nueva partida ─(¿sustituir?)─► Plano de entrada ─► Atrio 1
       ─ Ajustes · Controles · Créditos · Salir
Sala ─ Esc/P ─► Pausa ─ Reanudar · Volver al último brasero · Ajustes · Controles · Volver al título
Arena ─ victoria ─► Epílogo ─► Título («Partida completada»)
```

## Archivos

| Archivo | Qué hace |
| --- | --- |
| `Scripts/Save/SaveGame.gd` | Ranura única versionada, escritura segura (temporal, `.bak` y reemplazo) y validación que nunca lanza: OK, falta, dañado, otra versión o sala inexistente |
| `Scripts/Save/GameSettings.gd` | Preferencias en `settings.cfg`: volúmenes por bus, pantalla completa y efectos reducidos |
| `Scripts/UI/MenuPanel.gd`, `MenuPanels.gd` | Base de panel navegable con teclado; Ajustes, Controles, Créditos y Confirmación |
| `Scripts/UI/TitleScreen.gd`, `Scenes/UI/Title.tscn` | Título (escena principal) con el estado del guardado |
| `Scripts/UI/PauseMenu.gd` | Pausa sobre el árbol detenido |
| `Scripts/GameSession.gd` | `continue_game`, `pause_game`, `resume_game`, `restart_from_checkpoint`, `go_to_title`, `save_progress` |
| `Themes/baldwin_ui.tres` | Botones con foco de brasa, estado desactivado y deslizadores |

## Verificación

| Comprobación | Resultado |
| --- | --- |
| `tools/smoke.sh` y `--self-test` | OK |
| Etapas 1, 2, 3, 4 y 5 | 62/0, 61/0, 64/0, 18/0, 45/0 |
| Etapa 6 (`Tests/stage6_tests.gd`) | 54/0 |

La prueba de la etapa 6 recorre el flujo con pulsaciones del InputMap, en una carpeta propia que no toca la partida real. Cubre los casos que pide el roadmap:
- **Ciclo de guardado:** primera ejecución, guardar, salir, «cerrar y reabrir» (borra la memoria y continúa desde disco), carga repetida sin duplicados y partida completada.
- **Archivos problemáticos:** incompleto, versión desconocida, sala que ya no existe, objeto que ya no existe, escritura interrumpida y principal dañado con copia buena.
- **Interrupciones:** morir con la pausa abierta (el reintento espera), pausar durante un cambio de sala (no se permite), mantener una tecla al pausar y soltarla en pausa, y reanudar con Espacio sin que salte.
- **Ajustes y teclado:** persistencia de ajustes, ajustes dañados y navegación completa por los menús.

Capturas a 640×360 en `capturas/` (pausa, ajustes, controles, título con partida, confirmación, créditos y título con guardado dañado); hojas en `hoja_menus.png` y `hoja_menus_grises.png`. Se reproducen con `"$GODOT" --path . -s res://tools/stage6_capture.gd`. A 1280×720 y 1920×1080 el proyecto amplía este mismo render por un factor entero.

## Fallos encontrados y corregidos

- Tras llegar a una escena que no es sala (título, intro o epílogo), `GameSession` seguía creyéndose en mitad de un cambio y rechazaba «Continuar». Ahora el indicador se libera al terminar cualquier cambio de escena.
- Abrir una sala suelta (F6 o el smoke) empezaba una partida y habría sobrescrito la del jugador. Ahora sólo se guardan las partidas empezadas desde el título.
- `JSON.parse_string` escribía un `ERROR` en el log con cada archivo dañado. Se usa el parser de instancia, que sólo devuelve el código.

## Pendiente

- Probar pantalla completa y las tres resoluciones en una pantalla real (Windows en la etapa 7). En headless no hay ventana y aquí sólo se comprobó a 640×360 en ventana.
- Repetir en la build exportada el ciclo de guardar, cerrar, abrir y continuar (etapa 7).
- No hay remapeo de teclas: Controles sólo las muestra.
- Ratón: los botones lo admiten, pero el diseño y las pruebas son de teclado.
