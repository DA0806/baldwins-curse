extends SceneTree
## Capturas de la campaña (etapa 5) con el juego detenido. Necesita ventana.
##
##   godot --path . -s res://tools/stage5_capture.gd

const OUT := "res://docs/etapa5/capturas/"

var session: RunSession
var player: CharacterBody2D
var room: Node

func _initialize() -> void:
	_run()

func _run() -> void:
	await process_frame
	session = root.get_node("GameSession")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	session.start_campaign()
	await _wait("Intro")
	await _frames(100)
	await _save("01_intro")

	session.new_run()
	await _wait("Atrio1")
	player.inventory.from_state({"weapons": ["copper_sword", ""], "masks": []})
	await _place(Vector2(380, 224))
	player.execute_attack(0)
	for i in 30:
		await physics_frame
		if player.attack.phase == MeleeAttack.Phase.ACTIVE:
			break
	await _save("02_atrio_baldwin_tajo")

	var full := {"weapons": ["copper_sword", "crypt_mace"], "masks": ["mask_vow", "mask_ember"]}
	await _go("cripta_1", "checkpoint_cripta_1", full)
	await _place(Vector2(260, 224), 20)
	await _save("03_cripta_inscripcion")

	await _go("cripta_3", "checkpoint_cripta_3", full)
	var acolyte = room.get_node("Acolyte")
	await _place(Vector2(acolyte.global_position.x - 150, 224))
	await _until(func(): return acolyte.state == RangedEnemy.State.TELL)
	await _frames(10)
	await _save("04_cripta_acolito_anticipa")
	await _until(func(): return acolyte.state == RangedEnemy.State.RECOVER)
	await _save("05_cripta_brasa_en_vuelo")

	await _go("capilla_1", "from_cripta_4", full)
	var sealed = room.get_node("SealedCustodian")
	await _place(Vector2(sealed.global_position.x - 40, 224))
	await _until(func(): return sealed.attack.phase == MeleeAttack.Phase.STARTUP)
	await _frames(8)
	await _save("06_capilla_sellado_anticipa")

	await _go("capilla_3", "from_capilla_2", full)
	var boss: Boss = room.get_node("Encounter/Abbot")
	await _place(Vector2(boss.global_position.x - 120, 224))
	await _until(func(): return boss.state == Boss.State.SWEEP_TELL, 600)
	await _frames(20)
	await _save("07_abad_anticipa_tajo")
	await _until(func(): return boss.state == Boss.State.SWEEP_RECOVER)
	await _frames(6)
	await _save("08_abad_vulnerable_tajo")
	await _until(func(): return boss.state == Boss.State.RAIN_TELL, 600)
	await _frames(20)
	await _save("09_abad_lluvia_marcas")
	await _until(func(): return boss.state == Boss.State.EXHAUSTED, 300)
	await _frames(6)
	await _save("10_abad_agotado")

	boss.health.take_damage(100000.0)
	await _frames(10)
	var previous := room.get_instance_id()
	player.respawn_at(Vector2(928, 224))
	await _wait("Ending", previous)
	await _frames(30)
	await _save("11_epilogo")
	quit()

func _frames(count: int) -> void:
	for i in count:
		await process_frame

func _until(condition: Callable, limit: int = 400) -> void:
	for i in limit:
		if condition.call():
			return
		if player and is_instance_valid(player):
			player.health.reset() # que el jugador aguante mientras se encuadra
		await physics_frame

func _wait(expected: String, previous_id: int = 0) -> void:
	for i in 600:
		await process_frame
		var scene := current_scene
		if scene and scene.get_instance_id() != previous_id and scene.name == expected and scene.is_node_ready():
			room = scene
			var found = scene.get_node_or_null("CharacterBody2D")
			if found:
				player = found
			await _frames(30)
			return

func _go(room_id: String, spawn_id: String, state: Dictionary) -> void:
	player.inventory.from_state(state)
	var previous := room.get_instance_id()
	session.travel(room_id, spawn_id, player)
	await _wait(String(session.ROOMS[room_id]).get_file().get_basename(), previous)

func _place(at: Vector2, settle: int = 30) -> void:
	player.respawn_at(at)
	for i in settle:
		await physics_frame

func _save(name: String) -> void:
	paused = true
	await _frames(3)
	root.get_texture().get_image().save_png(ProjectSettings.globalize_path(OUT + name + ".png"))
	paused = false
