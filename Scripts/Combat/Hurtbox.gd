class_name Hurtbox
extends Area2D

## Zona vulnerable. No detecta nada por sí misma: las zonas de golpe (Hitbox)
## la encuentran por capa y le entregan el daño, que resuelve su Health.

@export var health: Health

func _ready() -> void:
	monitoring = false

## Devuelve el daño realmente aplicado (0 si no hubo efecto).
func receive_hit(damage: float, attacker: Node = null) -> float:
	if not health:
		return 0.0
	return health.take_damage(damage, attacker)

func set_enabled(enabled: bool) -> void:
	set_deferred("monitorable", enabled)

func _draw() -> void:
	if not Hitbox.debug_draw:
		return
	for child in get_children():
		var shape := child as CollisionShape2D
		if shape and shape.shape is RectangleShape2D:
			var size: Vector2 = (shape.shape as RectangleShape2D).size
			draw_rect(Rect2(shape.position - size / 2.0, size), Color(0.3, 1.0, 0.4, 0.8), false, 1.0)
