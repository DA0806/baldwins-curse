extends SceneTree
## Capturas de la sala de referencia (Atrio 2) con el juego detenido.
## Necesita ventana (no headless). Escribe PNG de 640x360 en docs/etapa4/capturas;
## tools/stage4_sheets.py genera después las versiones x2, x3 y en escala de grises.
##
##   godot --path . -s res://tools/stage4_capture.gd

const OUT := "res://docs/etapa4/capturas/"

var session: RunSession
var player: CharacterBody2D

func _initialize() -> void:
	_run()

func _run() -> void:
	await process_frame
	session = root.get_node("GameSession")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	session.new_run()
	await _wait_scene("Atrio1")
	player.inventory.from_state({"weapons": ["copper_sword", ""], "masks": ["mask_vow"]})
	session.travel("atrio_2", "from_atrio_1", player)
	var room := await _wait_scene("Atrio2")

	# 1. Inicio: brasero (encendido al tocarlo), candelabros y borde del foso.
	player.respawn_at(Vector2(150, 224))
	for i in 10:
		await physics_frame
	await _shot(Vector2(330, 224), "01_brasero_foso")
	# 2. Foso con púas (peligro) y pedestal con la máscara (pickup).
	await _shot(Vector2(560, 224), "02_foso_pickup")
	# 3. Custodio en anticipación (hoja en alto, ojos encendidos, "!").
	var enemy = room.get_node("GroundEnemy")
	player.respawn_at(enemy.global_position + Vector2(-36, -8))
	for i in 240:
		await physics_frame
		if enemy.attack.phase == MeleeAttack.Phase.STARTUP:
			break
	await _freeze_and_save("03_anticipacion")
	# 4. Golpe del custodio.
	for i in 120:
		await physics_frame
		if enemy.attack.phase == MeleeAttack.Phase.ACTIVE:
			break
	await _freeze_and_save("04_golpe")
	# 5. Salida: arco encendido y estandartes con chevrón.
	enemy.queue_free()
	await _shot(Vector2(1120, 224), "05_salida")
	quit()

func _wait_scene(expected: String) -> Node:
	for i in 600:
		await process_frame
		var scene := current_scene
		if scene and scene.name == expected and scene.is_node_ready():
			await physics_frame
			player = scene.get_node("CharacterBody2D")
			return scene
	return null

func _shot(at: Vector2, name: String) -> void:
	player.respawn_at(at)
	for i in 30:
		await physics_frame
	await _freeze_and_save(name)

## Pausa el árbol (juego detenido), deja dibujar y guarda.
func _freeze_and_save(name: String) -> void:
	paused = true
	for i in 3:
		await process_frame
	root.get_texture().get_image().save_png(ProjectSettings.globalize_path(OUT + name + ".png"))
	paused = false
