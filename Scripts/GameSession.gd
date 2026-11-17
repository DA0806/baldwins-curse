class_name RunSession
extends Node

## Estado de la partida en memoria (autoload "GameSession").
## Se accede con RunSession.of(nodo): los scripts lanzados con `-s` (pruebas)
## no ven los autoloads como identificadores globales.
##
## Contrato de estado: sólo datos simples con IDs estables. Salas por
## `room_id` (ROOMS), puntos de aparición por `spawn_id` (nombre del nodo dentro
## de `Spawns` en la sala), objetos por ID de ItemCatalog y recogidas únicas por
## `unique_id` del pickup. Nunca guarda nodos ni rutas de escena arbitrarias.
## La etapa 6 escribirá `checkpoint` a disco con este mismo formato.
##
##   {
##     "version": 1,
##     "room_id": "atrio_2",
##     "spawn_id": "checkpoint_atrio_2",
##     "health": 100.0,
##     "inventory": {"weapons": ["copper_sword", ""], "swap_slot": 0,
##                   "masks": ["mask_vow"], "active_mask": 0},
##     "collected": ["atrio_1/copper_sword", "atrio_1/mask_vow"],
##   }

signal checkpoint_activated(room_id: String, spawn_id: String)
signal run_finished

const STATE_VERSION: int = 1
const FIRST_ROOM: String = "atrio_1"
const START_SPAWN: String = "start"
## Ruta de la campaña (docs/etapa5/ruta.md). Los IDs son el contrato del guardado.
const ROOMS: Dictionary = {
	"atrio_1": "res://Scenes/Rooms/Atrio1.tscn",
	"atrio_2": "res://Scenes/Rooms/Atrio2.tscn",
	"atrio_3": "res://Scenes/Rooms/Atrio3.tscn",
	"cripta_1": "res://Scenes/Rooms/Cripta1.tscn",
	"cripta_2": "res://Scenes/Rooms/Cripta2.tscn",
	"cripta_3": "res://Scenes/Rooms/Cripta3.tscn",
	"cripta_4": "res://Scenes/Rooms/Cripta4.tscn",
	"capilla_1": "res://Scenes/Rooms/Capilla1.tscn",
	"capilla_2": "res://Scenes/Rooms/Capilla2.tscn",
	"capilla_3": "res://Scenes/Rooms/Capilla3.tscn",
}
## Plano de entrada (motivación de Baldwin) y epílogo de victoria.
const INTRO_SCENE: String = "res://Scenes/Intro.tscn"
const TITLE_SCENE: String = "res://Scenes/UI/Title.tscn"
const ENDING_SCENE: String = "res://Scenes/Ending.tscn"
## Fundido a negro de cada cambio de sala (salida, reaparición, final).
const FADE_TIME: float = 0.25
## Fundido del ambiente al entrar o salir de una sala con otro ambiente.
const AMBIENCE_FADE: float = 0.8

var run_active: bool = false
var finished: bool = false
## Recogidas únicas de la partida en curso: unique_id -> true.
var collected: Dictionary = {}
## Última activación de un punto de control.
var checkpoint: Dictionary = {}
var retries: int = 0
var run_time: float = 0.0
## Escribe el progreso en disco (SaveGame) al empezar, al encender un brasero y al terminar.
var save_enabled: bool = true
## Sólo las partidas empezadas con new_run() o continue_game() se guardan. Abrir
## una sala suelta (F6 en el editor, el smoke) no pisa la partida del jugador.
var _persist: bool = false
var pause_menu: PauseMenu

## Estado que aplicará la próxima sala al cargar (viaje o restauración).
var _pending: Dictionary = {}
## Evita encadenar dos cambios de escena (p. ej. caer mientras se cruza una salida).
var _changing: bool = false
var _fade_rect: ColorRect
var _ambience: AudioStreamPlayer
var _ambience_tween: Tween

func _ready() -> void:
	# Sigue activo con el árbol en pausa: abre y cierra el menú de pausa y funde.
	process_mode = Node.PROCESS_MODE_ALWAYS
	GameSettings.load_settings()
	var layer := CanvasLayer.new()
	layer.layer = 100
	add_child(layer)
	_fade_rect = ColorRect.new()
	_fade_rect.color = Color(0.082, 0.098, 0.141, 0.0)
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	layer.add_child(_fade_rect)
	_ambience = AudioStreamPlayer.new()
	_ambience.bus = &"Music"
	_ambience.finished.connect(_ambience.play) # bucle
	add_child(_ambience)

## F3 (sólo en builds de depuración) muestra u oculta zonas de golpe y vulnerables.
func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause") and not event.is_echo() and can_pause():
		get_viewport().set_input_as_handled()
		pause_game()
		return
	var key := event as InputEventKey
	if OS.is_debug_build() and key and key.pressed and not key.echo and key.keycode == KEY_F3:
		Hitbox.debug_draw = not Hitbox.debug_draw
		get_tree().root.propagate_call(&"queue_redraw")

## Ambiente de la sala. Si cambia, el anterior se apaga y el nuevo entra con
## fundido; si es el mismo, sigue sonando sin cortes entre salas.
func set_ambience(stream: AudioStream) -> void:
	if stream == _ambience.stream and (stream == null or _ambience.playing):
		return
	if _ambience_tween:
		_ambience_tween.kill()
	_ambience_tween = create_tween()
	if _ambience.playing:
		_ambience_tween.tween_property(_ambience, "volume_db", -40.0, AMBIENCE_FADE * 0.5)
	_ambience_tween.tween_callback(_swap_ambience.bind(stream))
	if stream:
		_ambience_tween.tween_property(_ambience, "volume_db", 0.0, AMBIENCE_FADE)

func _swap_ambience(stream: AudioStream) -> void:
	_ambience.stream = stream
	if stream and DisplayServer.get_name() != "headless": # como SoundBank: sin audio en headless
		_ambience.volume_db = -40.0
		_ambience.play()
	else:
		_ambience.stop()

## Al cerrar el juego: el ambiente se detiene para no retener su recurso.
func _exit_tree() -> void:
	_ambience.stop()
	_ambience.stream = null

func current_ambience() -> AudioStream:
	return _ambience.stream

const NODE_PATH: NodePath = ^"/root/GameSession"

static func of(node: Node) -> RunSession:
	return node.get_node_or_null(NODE_PATH) as RunSession

func _physics_process(delta: float) -> void:
	if run_active and not finished and not get_tree().paused:
		run_time += delta

# ---------------------------------------------------------------- estado

func capture(room_id: String, spawn_id: String, player: Node, health_value: float) -> Dictionary:
	return {
		"version": STATE_VERSION,
		"room_id": room_id,
		"spawn_id": spawn_id,
		"health": health_value,
		"inventory": player.inventory.to_state(),
		"collected": collected.keys(),
	}

func is_collected(unique_id: String) -> bool:
	return collected.has(unique_id)

func mark_collected(unique_id: String) -> void:
	if not unique_id.is_empty():
		collected[unique_id] = true

# ---------------------------------------------------------------- flujo

## La sala llama a esto en su _ready. Si llega un viaje o una restauración
## para ella, lo aplica; si no (arranque normal o F6), empieza partida aquí.
func enter_room(room: Node, player: Node) -> void:
	_changing = false
	set_ambience(room.ambience)
	var state: Dictionary = _pending
	_pending = {}
	if state.is_empty() or state.get("room_id") != room.room_id:
		_start_run(room, player)
		return
	player.inventory.from_state(state.get("inventory", {}))
	player.health.set_current(float(state.get("health", player.health.max_health)))
	player.respawn_at(room.get_spawn_position(String(state.get("spawn_id", START_SPAWN))))

func _start_run(room: Node, player: Node) -> void:
	run_active = true
	finished = false
	retries = 0
	run_time = 0.0
	collected.clear()
	checkpoint = capture(room.room_id, START_SPAWN, player, player.health.max_health)
	save_progress()

func save_progress() -> void:
	if save_enabled and _persist:
		SaveGame.write(self)

## Guarda el estado actual con salud completa de reaparición.
func activate_checkpoint(room: Node, player: Node, spawn_id: String) -> void:
	if not run_active or _changing or player.health.is_dead():
		return
	checkpoint = capture(room.room_id, spawn_id, player, player.health.max_health)
	save_progress()
	checkpoint_activated.emit(room.room_id, spawn_id)

func is_active_checkpoint(room_id: String, spawn_id: String) -> bool:
	return checkpoint.get("room_id") == room_id and checkpoint.get("spawn_id") == spawn_id

## Muerte o caída: vuelve a la última activación. La sala se recarga, así que
## enemigos y objetos transitorios vuelven a su estado inicial; las recogidas
## únicas guardadas no reaparecen.
func restore_checkpoint() -> bool:
	if checkpoint.is_empty() or _changing:
		return false
	retries += 1
	collected.clear()
	for unique_id in checkpoint.get("collected", []):
		collected[unique_id] = true
	_pending = checkpoint.duplicate(true)
	return _change_scene(ROOMS.get(checkpoint.get("room_id"), ""))

## Cruce de salida: lleva el estado actual (con la salud actual) a otra sala.
func travel(room_id: String, spawn_id: String, player: Node) -> bool:
	if _changing or not ROOMS.has(room_id):
		return false
	_pending = capture(room_id, spawn_id, player, player.health.current)
	return _change_scene(ROOMS[room_id])

func finish_run() -> void:
	if _changing or finished:
		return
	finished = true
	save_progress()
	run_finished.emit()
	set_ambience(null)
	_change_scene(ENDING_SCENE)

## Continúa desde la última activación guardada. Devuelve false si el archivo
## no permite continuar (falta, dañado, otra versión, completado...).
func continue_game() -> bool:
	var result := SaveGame.load_game()
	if not result.can_continue() or _changing:
		return false
	var data: Dictionary = result.data
	checkpoint = data.checkpoint
	run_active = true
	finished = false
	retries = int(data.get("retries", 0))
	run_time = float(data.get("run_time", 0.0))
	collected.clear()
	for unique_id in checkpoint.get("collected", []):
		collected[String(unique_id)] = true
	_pending = checkpoint.duplicate(true)
	_persist = true
	return _change_scene(ROOMS[checkpoint.room_id])

# ---------------------------------------------------------------- pausa

## Sólo se pausa dentro de una sala jugable y fuera de un cambio de escena.
func can_pause() -> bool:
	var scene := get_tree().current_scene
	return not get_tree().paused and not _changing and scene != null and scene.get("room_id") != null \
		and scene.get_tree().get_first_node_in_group("player") != null

func pause_game() -> void:
	get_tree().paused = true
	pause_menu = PauseMenu.new()
	add_child(pause_menu)

## Cierra la pausa y deja pasar dos cuadros antes de devolver el control: la
## tecla que confirmó "Reanudar" (Espacio también salta) no llega al jugador.
func resume_game() -> void:
	if is_instance_valid(pause_menu):
		pause_menu.queue_free()
	pause_menu = null
	await get_tree().process_frame
	await get_tree().process_frame
	get_tree().paused = false

func _close_pause() -> void:
	if is_instance_valid(pause_menu):
		pause_menu.queue_free()
	pause_menu = null
	get_tree().paused = false

func restart_from_checkpoint() -> void:
	_close_pause()
	restore_checkpoint()

## Vuelve al título. El progreso ya está guardado en el último brasero.
func go_to_title() -> void:
	_close_pause()
	run_active = false
	_changing = false
	_change_scene(TITLE_SCENE)

## Campaña desde el principio: plano de entrada y después new_run().
## Es el punto de conexión del menú de la etapa 6.
func start_campaign() -> void:
	run_active = false
	finished = false
	_changing = false
	set_ambience(null)
	_change_scene(INTRO_SCENE)

## Partida nueva desde la primera sala, sin estado previo.
func new_run() -> void:
	_persist = true
	run_active = false
	finished = false
	checkpoint = {}
	collected.clear()
	_pending = {}
	_changing = false
	_change_scene(ROOMS[FIRST_ROOM])

func _change_scene(path: String) -> bool:
	if path.is_empty() or _changing:
		return false
	_changing = true
	_transition(path)
	return true

func _transition(path: String) -> void:
	var tween := create_tween()
	tween.tween_property(_fade_rect, "color:a", 1.0, FADE_TIME)
	await tween.finished
	get_tree().change_scene_to_file(path)
	await get_tree().process_frame
	await get_tree().process_frame
	# Las escenas que no son salas (título, intro, epílogo) no pasan por enter_room.
	_changing = false
	create_tween().tween_property(_fade_rect, "color:a", 0.0, FADE_TIME)
