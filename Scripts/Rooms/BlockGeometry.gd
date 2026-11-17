extends StaticBody2D

## Geometría de sala: cada rectángulo es a la vez colisión y dibujo, así que la
## superficie visible coincide siempre con la sólida. Sin texturas es un bloque
## de color (salas provisionales); con fill/top_texture dibuja tiles de 16 px
## alineados al origen del bloque (sala de referencia, etapa 4).

@export var blocks: Array[Rect2] = []
@export var color: Color = Color("303b4a")
## Textura de relleno en mosaico (16 px). Sin ella se dibuja `color`.
@export var fill_texture: Texture2D
## Franja superior de 16 px (borde pisable). Sólo con fill_texture.
@export var top_texture: Texture2D

func _ready() -> void:
	for rect in blocks:
		var shape := RectangleShape2D.new()
		shape.size = rect.size
		var collision := CollisionShape2D.new()
		collision.shape = shape
		collision.position = rect.get_center()
		add_child(collision)
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	queue_redraw()

func _draw() -> void:
	for rect in blocks:
		if not fill_texture:
			draw_rect(rect, color)
			continue
		draw_texture_rect(fill_texture, rect, true)
		if top_texture:
			draw_texture_rect(top_texture, Rect2(rect.position, Vector2(rect.size.x, minf(16.0, rect.size.y))), true)
