extends SceneTree
## Recorrido guiado de la sala de referencia para grabarlo con Movie Maker.
## Pulsa las mismas acciones del InputMap que un jugador; no mueve nada a mano
## salvo el punto de partida.
##
##   godot --path . --write-movie /ruta/cuadros/f.png -s res://tools/stage4_demo.gd
##   swift tools/frames_to_mp4.swift /ruta/cuadros /ruta/cuadros/f.wav salida.mp4

var session: RunSession
var player: CharacterBody2D
var room: Node

func _initialize() -> void:
	_run()

func _run() -> void:
	await process_frame
	session = root.get_node("GameSession")
	session.new_run()
	await _wait_scene("Atrio1")
	player.inventory.from_state({"weapons": ["copper_sword", ""], "masks": ["mask_vow"]})
	player.respawn_at(Vector2(1120, 224))
	await _ticks(100)

	# Salida del Atrio 1: fundido y entrada del ambiente.
	_press(&"move_right", true)
	await _wait_scene("Atrio2")
	await _ticks(60) # la sala con su ambiente
	await _walk_to(150) # enciende el brasero
	await _ticks(90)

	# Caída al foso: vuelve al brasero con fundido.
	await _walk_to(430)
	await _wait_scene("Atrio2", room.get_instance_id())
	await _ticks(90)

	# Salto largo sobre el foso.
	_press(&"move_right", true)
	await _until(func(): return player.global_position.x >= 396.0)
	_press(&"jump", true)
	await _ticks(20)
	_press(&"jump", false)
	await _until(func(): return player.global_position.x >= 690.0)
	_press(&"move_right", false)
	await _ticks(20)

	# Recoger el Ascua y alternar máscaras (recarga visible en el HUD).
	await _tap(&"interact")
	await _ticks(80)
	for action in [&"next_mask", &"prev_mask", &"next_mask", &"prev_mask"]:
		await _tap(action)
		await _ticks(75) # la recarga de 1 s se vacía en el HUD
	await _ticks(30)

	# Acercarse con el Voto y dejar que el custodio anticipe y golpee.
	var enemy = room.get_node("GroundEnemy")
	await _walk_to(enemy.global_position.x - 32.0)
	await _until(func(): return enemy.attack.phase == MeleeAttack.Phase.RECOVERY, 240)
	await _ticks(20)

	# Esquiva: al ver la siguiente anticipación retrocede y el golpe falla.
	await _until(func(): return enemy.attack.phase == MeleeAttack.Phase.STARTUP, 300)
	await _ticks(6)
	_press(&"move_left", true)
	await _ticks(26)
	_press(&"move_left", false)
	await _until(func(): return enemy.attack.phase == MeleeAttack.Phase.RECOVERY, 120)
	await _ticks(10)

	# Ascua y combate hasta derribarlo.
	await _tap(&"next_mask")
	for i in 900:
		if enemy.health.is_dead():
			break
		var gap: float = enemy.global_position.x - player.global_position.x
		_press(&"move_right", gap > 30.0)
		_press(&"move_left", gap < -30.0)
		if absf(gap) <= 30.0 and player.attack.can_start():
			await _tap(&"attack_weapon_1")
		await physics_frame
	_press(&"move_right", false)
	_press(&"move_left", false)
	await _ticks(90)

	# Salida al Atrio 3: fundido y el ambiente se apaga.
	_press(&"move_right", true)
	await _wait_scene("Atrio3")
	_press(&"move_right", false)
	await _ticks(240)
	quit()

# ---------------------------------------------------------------- utilidades

func _press(action: StringName, pressed: bool) -> void:
	if Input.is_action_pressed(action) == pressed:
		return
	var event := InputEventAction.new()
	event.action = action
	event.pressed = pressed
	Input.parse_input_event(event)

func _tap(action: StringName) -> void:
	_press(action, true)
	await _ticks(3)
	_press(action, false)
	await _ticks(1)

func _ticks(count: int) -> void:
	for i in count:
		await physics_frame

func _until(condition: Callable, limit: int = 600) -> void:
	for i in limit:
		if condition.call():
			return
		await physics_frame

func _walk_to(x: float) -> void:
	_press(&"move_right", true)
	await _until(func(): return not is_instance_valid(player) or player.global_position.x >= x)
	_press(&"move_right", false)

func _wait_scene(expected: String, previous_id: int = 0) -> void:
	for i in 600:
		await process_frame
		var scene := current_scene
		if scene and scene.get_instance_id() != previous_id and scene.name == expected and scene.is_node_ready():
			room = scene
			player = scene.get_node("CharacterBody2D")
			await physics_frame
			return
