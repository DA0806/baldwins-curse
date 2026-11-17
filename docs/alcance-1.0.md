# Alcance de trabajo propuesto para la 1.0

Propuesta de partida tomada del roadmap. Destino, duración, nombres y reglas de las máscaras son decisiones propuestas a partir del código disponible; quien dirige el proyecto puede cambiarlas.

## Qué es la 1.0

Una aventura de plataformas y acción 2D para una persona, corta (20–35 minutos en una primera partida).

| Contenido | Cantidad |
| --- | --- |
| Zonas | 3 (Atrio del Voto, Cripta de las Ascuas, Capilla del Último Sello), unas diez salas contando la arena final |
| Armas | 2 |
| Máscaras jugables | 2 (Máscara del Voto, Máscara de Ascua) |
| Enemigos base | 2 |
| Variante de enemigo | 1 |
| Jefe | 1 |
| Cierre | 1 epílogo |

## Destino y controles

- **Plataforma inicial:** Windows x64. Debe probarse en un equipo real; hasta ahora sólo se ha ejecutado en macOS Apple Silicon.
- **Entrada:** teclado. `←`/`→` caminar, `Espacio`/`↑` saltar, `R` recoger, `Z`/`X` atacar con la ranura 1/2, `C`/`V` cambiar de máscara.
- **Motor:** Godot 4.7.x Standard con GDScript. Línea base probada: 4.7.2 (`ed1daf0bf`).
- **Presentación:** viewport de 640×360 con escala entera y filtrado nearest.

## Política de reintento

Cada reintento (muerte o caída) recupera el estado de la **última activación de un punto de control**: sala, salud de reaparición, armas, máscaras y recogidas únicas.

En la etapa 1 sólo existe la reaparición por caída en la sala de pruebas, que devuelve al jugador al punto de aparición y conserva su inventario. Los puntos de control llegan en la etapa 3 y el guardado en disco en la etapa 6.

## Fuera de la 1.0 (P2)

Soltar armas manualmente, más efectos y cadenas de combo, máscaras adicionales, rutas opcionales, mando, web y logros.
