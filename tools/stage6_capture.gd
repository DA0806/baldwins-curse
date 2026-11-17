extends SceneTree
## Capturas de los menús (etapa 6) a 640x360. Necesita ventana. Usa una carpeta
## de guardado propia (user://capture_stage6/) para no tocar la partida real.
##
##   godot --path . -s res://tools/stage6_capture.gd

const OUT := "res://docs/etapa6/capturas/"

var session: RunSession

func _initialize() -> void:
	_run()

func _run() -> void:
	await process_frame
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	SaveGame.directory = "user://capture_stage6/"
	SaveGame.delete_all()
	session = root.get_node("GameSession")

	# Partida en la Cripta para que el título tenga algo que resumir.
	session.new_run()
	await _wait("Atrio1")
	var player = current_scene.get_node("CharacterBody2D")
	player.inventory.from_state({"weapons": ["copper_sword", "crypt_mace"], "masks": ["mask_vow", "mask_ember"]})
	session.run_time = 754.0
	session.travel("cripta_3", "checkpoint_cripta_3", player)
	await _wait("Cripta3")
	await _frames(20)
	await _tap(&"pause")
	await _save("01_pausa")
	await _tap(&"ui_down")
	await _tap(&"ui_down")
	await _tap(&"ui_accept")
	await _save("02_ajustes")
	await _tap(&"ui_cancel")
	await _tap(&"ui_down")
	await _tap(&"ui_accept")
	await _save("03_controles")
	await _tap(&"ui_cancel")

	session.go_to_title()
	await _wait("TitleScreen")
	await _save("04_titulo_con_partida")
	await _tap(&"ui_down")
	await _tap(&"ui_accept")
	await _save("05_confirmar_nueva_partida")
	await _tap(&"ui_cancel")
	for i in 3:
		await _tap(&"ui_down")
	await _tap(&"ui_accept")
	await _save("06_creditos")
	await _tap(&"ui_cancel")

	var file := FileAccess.open(SaveGame.path(), FileAccess.WRITE)
	file.store_string("{dañado")
	file.close()
	DirAccess.remove_absolute(SaveGame.path() + ".bak")
	session.go_to_title()
	await _wait("TitleScreen")
	await _save("07_titulo_guardado_danado")
	SaveGame.delete_all()
	quit()

func _frames(count: int) -> void:
	for i in count:
		await process_frame

func _tap(action: StringName) -> void:
	for pressed in [true, false]:
		var event := InputEventAction.new()
		event.action = action
		event.pressed = pressed
		Input.parse_input_event(event)
		await _frames(3)

func _wait(expected: String) -> void:
	# Espera a una instancia nueva: del título al título el nombre no cambia.
	var previous := current_scene.get_instance_id() if current_scene else 0
	for i in 600:
		await process_frame
		var scene := current_scene
		if scene and scene.get_instance_id() != previous and scene.name == expected and scene.is_node_ready():
			await _frames(40)
			return

func _save(name: String) -> void:
	await _frames(4)
	root.get_texture().get_image().save_png(ProjectSettings.globalize_path(OUT + name + ".png"))
