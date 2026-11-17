class_name Health
extends Node

## Salud de un personaje. Único lugar donde se resuelve el daño recibido.

signal health_changed(current: float, maximum: float)
signal damaged(amount: float, source: Node)
signal died(source: Node)

@export var max_health: float = 100.0
## Segundos sin recibir daño después de un impacto.
@export var invulnerability_time: float = 0.0

var current: float = 0.0
var invulnerable_left: float = 0.0
## Filtro opcional del daño entrante (amount -> amount). El jugador lo usa
## para la máscara defensiva; es el único sitio donde se modifica.
var damage_modifier: Callable

func _ready() -> void:
	current = max_health

func _physics_process(delta: float) -> void:
	if invulnerable_left > 0.0:
		invulnerable_left = maxf(0.0, invulnerable_left - delta)

func is_dead() -> bool:
	return current <= 0.0

## Aplica daño y devuelve cuánto se aplicó de verdad.
func take_damage(amount: float, source: Node = null) -> float:
	if damage_modifier.is_valid():
		amount = damage_modifier.call(amount)
	if amount <= 0.0 or is_dead() or invulnerable_left > 0.0:
		return 0.0
	var dealt: float = minf(amount, current)
	current -= dealt
	invulnerable_left = invulnerability_time
	health_changed.emit(current, max_health)
	damaged.emit(dealt, source)
	if is_dead():
		died.emit(source)
	return dealt

## Fija la salud (restaurar estado tras cambiar de sala). Se limita a (0, max].
func set_current(value: float) -> void:
	current = clampf(value, 1.0, max_health)
	invulnerable_left = 0.0
	health_changed.emit(current, max_health)

func reset() -> void:
	current = max_health
	invulnerable_left = 0.0
	health_changed.emit(current, max_health)
