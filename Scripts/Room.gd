extends Node2D

## Sala jugable: limita la cámara del jugador a su rectángulo y gestiona caídas
## y muertes. Con `room_id` vacío es un laboratorio (world.tscn): la caída
## devuelve al SpawnPoint y la muerte reinicia el encuentro en sitio. Con
## `room_id` forma parte de la partida: la caída y la muerte restauran el último
## punto de control (GameSession).

signal player_respawned(player: Node2D)
signal player_retried(player: Node2D)

## Rectángulo de la sala en píxeles de mundo. La cámara no sale de aquí.
## ID estable de la sala (clave de RunSession.of(self).ROOMS). Vacío = laboratorio.
@export var room_id: String = ""

## Ambiente sonoro de la sala (bus Music). Vacío = silencio.
@export var ambience: AudioStream

@export var room_rect: Rect2i = Rect2i(0, 0, 1280, 360)

## Segundos entre la muerte del jugador y el reintento.
@export var retry_delay: float = 1.0

var respawn_count: int = 0
var retry_count: int = 0

@onready var spawn_point: Marker2D = $SpawnPoint
@onready var kill_zone: Area2D = $KillZone

func _ready() -> void:
	kill_zone.body_entered.connect(_on_kill_zone_body_entered)
	var player := get_tree().get_first_node_in_group("player")
	if player:
		apply_camera_limits(player)
		var health := player.get_node_or_null("Health") as Health
		if health:
			health.died.connect(_on_player_died.bind(player))
		if not room_id.is_empty():
			RunSession.of(self).enter_room(self, player)

## Posición de un punto de aparición por ID (nodo dentro de `Spawns`).
## Sin coincidencia, el SpawnPoint de la sala.
func get_spawn_position(spawn_id: String) -> Vector2:
	var node := get_node_or_null(NodePath("Spawns/" + spawn_id)) as Node2D
	return node.global_position if node else spawn_point.global_position

func _on_player_died(_source: Node, player: Node2D) -> void:
	# Conexión (no await): si la sala se libera antes, el temporizador no la toca.
	get_tree().create_timer(retry_delay, false, true).timeout.connect(_after_death.bind(player))

func _after_death(player: Node2D) -> void:
	if room_id.is_empty():
		retry(player)
	else:
		RunSession.of(self).restore_checkpoint()

## Reintento: todo lo del grupo "encounter" vuelve a su estado inicial y el
## jugador reaparece con la salud completa. El inventario se conserva.
func retry(player: Node2D) -> void:
	if not is_instance_valid(player):
		return
	get_tree().call_group(&"encounter", "reset_encounter")
	player.revive()
	player.respawn_at(spawn_point.global_position)
	retry_count += 1
	player_retried.emit(player)

func apply_camera_limits(player: Node) -> void:
	var camera := player.get_node_or_null("Camera2D") as Camera2D
	if not camera:
		return
	camera.limit_left = room_rect.position.x
	camera.limit_top = room_rect.position.y
	camera.limit_right = room_rect.end.x
	camera.limit_bottom = room_rect.end.y

func _on_kill_zone_body_entered(body: Node2D) -> void:
	if body.is_in_group("player") and body.has_method("respawn_at"):
		# Diferido: no se mueve un cuerpo durante el callback de física.
		_respawn.call_deferred(body)

func _respawn(player: Node2D) -> void:
	if not is_instance_valid(player):
		return
	respawn_count += 1
	if not room_id.is_empty():
		RunSession.of(self).restore_checkpoint()
		return
	player.respawn_at(spawn_point.global_position)
	player_respawned.emit(player)
