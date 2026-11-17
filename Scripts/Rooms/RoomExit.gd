extends Area2D

## Salida de sala. Lleva el estado actual a `target_room`/`target_spawn`, o
## termina la partida si `ends_run` está activo.

@export var target_room: String = ""
@export var target_spawn: String = "start"
@export var ends_run: bool = false
@export var size: Vector2 = Vector2(32, 96)
## Marco provisional. Se apaga cuando la sala pone su propio arco.
@export var draw_frame: bool = true

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2 # player
	var shape := RectangleShape2D.new()
	shape.size = size
	var collision := CollisionShape2D.new()
	collision.shape = shape
	add_child(collision)
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player") or body.health.is_dead():
		return
	if ends_run:
		RunSession.of(self).finish_run()
	else:
		RunSession.of(self).travel(target_room, target_spawn, body)

## Marco de puerta en marfil.
func _draw() -> void:
	if not draw_frame:
		return
	draw_rect(Rect2(-size / 2.0, size), Color("e5d6b3"), false, 2.0)
