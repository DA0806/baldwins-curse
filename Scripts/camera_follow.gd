extends Camera2D

@export_group("Look-Ahead (Desplazamiento)")
## Distancia en píxeles que la cámara mira hacia adelante
@export var look_ahead_distance: float = 64.0
## Velocidad de transición entre lados (más bajo = más suave)
@export var look_ahead_speed: float = 3.0
## Desplazamiento vertical constante (para ver un poco más arriba/abajo)
@export var vertical_offset: float = -20.0

@onready var player: CharacterBody2D = get_parent()

var target_offset_x: float = 0.0

func _ready() -> void:
	# Aseguramos suavizado de posición nativo
	position_smoothing_enabled = true
	offset = _clamp_offset_to_limits(Vector2(0.0, vertical_offset))

func _process(delta: float) -> void:
	if not player:
		return
	
	# 1. Determinar hacia dónde mira el personaje según su velocidad horizontal
	if player.velocity.x > 10.0:
		target_offset_x = look_ahead_distance
	elif player.velocity.x < -10.0:
		target_offset_x = -look_ahead_distance
	
	# 2. Transición suave del offset horizontal hacia el objetivo
	var desired := Vector2(lerp(offset.x, target_offset_x, look_ahead_speed * delta), vertical_offset)
	offset = _clamp_offset_to_limits(desired)

## Camera2D aplica `offset` después de los límites, así que la anticipación
## podría mostrar lo que hay fuera de la sala. Aquí se recorta para que la
## vista completa quede dentro de limit_left/top/right/bottom.
func _clamp_offset_to_limits(desired: Vector2) -> Vector2:
	var half: Vector2 = get_viewport_rect().size * 0.5 / zoom
	var base: Vector2 = get_screen_center_position() - offset # centro sin offset
	desired.x = _clamp_axis(desired.x, limit_left + half.x - base.x, limit_right - half.x - base.x)
	desired.y = _clamp_axis(desired.y, limit_top + half.y - base.y, limit_bottom - half.y - base.y)
	return desired

func _clamp_axis(value: float, low: float, high: float) -> float:
	if low > high: # la sala es más pequeña que la vista en este eje
		return (low + high) * 0.5
	return clampf(value, low, high)

## Coloca la cámara de inmediato sobre el jugador (reaparición, cambio de sala).
func snap_to_target() -> void:
	target_offset_x = 0.0
	offset = Vector2.ZERO
	reset_smoothing()
	offset = _clamp_offset_to_limits(Vector2(0.0, vertical_offset))
