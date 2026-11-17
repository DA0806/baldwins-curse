# Etapa 5 · Ruta de la campaña

```text
Intro ─► ATRIO DEL VOTO ──────────────► CRIPTA DE LAS ASCUAS ─────────────────────► CAPILLA DEL ÚLTIMO SELLO ───► Epílogo
         atrio_1   atrio_2   atrio_3    cripta_1  cripta_2  cripta_3  cripta_4    capilla_1  capilla_2  capilla_3
         espada    [P] Voto  [P] 2      [P] Ascua maza      [P]       custodio    custodio   [P]        Abad
         maniquí   foso      guardianes I         plataf.   acólito   + 2 acól.   sellado II III        Sellado
                   custodio  reja                 custodio            reja                  antesala   (jefe)
```

`[P]` = punto de control (cinco: `checkpoint_atrio_2`, `checkpoint_atrio_3`, `checkpoint_cripta_1`, `checkpoint_cripta_3`, `checkpoint_capilla_2`). `I`, `II`, `III` = inscripciones sobre la motivación de Baldwin.

| Zona | Enseña | Encuentros |
| --- | --- | --- |
| Atrio del Voto (3) | Salto, espada, primer enemigo, Máscara del Voto | Maniquí, custodio, dos guardianes |
| Cripta de las Ascuas (4) | Máscara de Ascua, segunda arma (Maza de la Cripta), enemigo a distancia | Custodio, acólito, custodio con dos acólitos |
| Capilla del Último Sello (3) | Variante (custodio sellado), punto antes del jefe | Custodio sellado, Abad Sellado |

**Medidas de diseño** (etapa 1): salto largo de 77 px de altura y 129 px de alcance a velocidad máxima. Huecos de 96 px como máximo y escalones de 64 px como máximo; las plataformas quedan a 48–64 px sobre el suelo.

**Contrato de salas** (etapa 3): cada sala es una escena con `Room.gd` y un `room_id` estable registrado en `GameSession.ROOMS`. Las llegadas son nodos en `Spawns/<spawn_id>`, las salidas son `RoomExit` hacia `target_room`/`target_spawn` y las recogidas únicas llevan `unique_id`. Morir o caer restaura el último punto. Al vencer al Abad se abre la salida al epílogo, que devuelve al inicio (en la etapa 6, al menú).
