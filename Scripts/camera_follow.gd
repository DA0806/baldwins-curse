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
	offset.y = vertical_offset

func _process(delta: float) -> void:
	if not player:
		return
	
	# 1. Determinar hacia dónde mira el personaje según su velocidad horizontal
	if player.velocity.x > 10.0:
		target_offset_x = look_ahead_distance
	elif player.velocity.x < -10.0:
		target_offset_x = -look_ahead_distance
	
	# 2. Transición suave del offset horizontal hacia el objetivo
	offset.x = lerp(offset.x, target_offset_x, look_ahead_speed * delta)
