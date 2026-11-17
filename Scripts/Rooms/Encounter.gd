extends Node2D

## Encuentro: agrupa enemigos (hijos con un nodo Health). Cuando caen todos,
## retira la reja (`gate`) y emite `cleared`. Morir recarga la sala, así que el
## encuentro vuelve a empezar completo.

signal cleared

@export var gate: Node

var remaining: int = 0

func _ready() -> void:
	for child in get_children():
		var health := child.get_node_or_null("Health") as Health
		if health:
			remaining += 1
			health.died.connect(_on_enemy_died, CONNECT_ONE_SHOT)

func is_cleared() -> bool:
	return remaining == 0

func _on_enemy_died(_source: Node) -> void:
	remaining -= 1
	if remaining == 0:
		if is_instance_valid(gate):
			gate.queue_free()
		cleared.emit()
