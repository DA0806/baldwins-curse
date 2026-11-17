extends SceneTree
## Verificaciones de la etapa 6 (menús, pausa, guardado y ajustes).
##
##   godot --headless --fixed-fps 60 --path . -s res://Tests/stage6_tests.gd
##
## Usa su propia carpeta (user://tests_stage6/): no toca la partida ni los
## ajustes reales del jugador.

const DIR := "user://tests_stage6/"

var session: RunSession
var player: CharacterBody2D
var room: Node
var checks := 0
var failures := 0

func _initialize() -> void:
	_run()

func _run() -> void:
	await process_frame
	SaveGame.directory = DIR
	SaveGame.delete_all()
	if FileAccess.file_exists(GameSettings.path()):
		DirAccess.remove_absolute(GameSettings.path())
	session = root.get_node_or_null("GameSession") as RunSession
	if not session:
		session = (load("res://Scripts/GameSession.gd") as GDScript).new()
		session.name = "GameSession"
		root.add_child(session)
	await _test_first_run_and_new_game()
	await _test_pause()
	await _test_title_continue_and_reopen()
	await _test_bad_files()
	await _test_completed_and_replace()
	await _test_settings()
	await _test_keyboard_menus()
	print("\n== %d comprobaciones, %d fallas ==" % [checks, failures])
	quit(1 if failures > 0 else 0)

# ---------------------------------------------------------------- utilidades

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures += 1
	print("  %s %s" % ["ok  " if condition else "FAIL", message])

func frames(count: int) -> void:
	for i in count:
		await process_frame

func ticks(count: int) -> void:
	for i in count:
		await physics_frame

func action(name: StringName, pressed: bool) -> void:
	var event := InputEventAction.new()
	event.action = name
	event.pressed = pressed
	Input.parse_input_event(event)

func tap(name: StringName) -> void:
	action(name, true)
	await frames(2)
	action(name, false)
	await frames(2)

## Pulsación real de una tecla (para comprobar que Espacio en un menú no salta).
func key(code: Key) -> void:
	for pressed in [true, false]:
		var event := InputEventKey.new()
		event.physical_keycode = code
		event.keycode = code
		event.pressed = pressed
		Input.parse_input_event(event)
		await frames(2)

func wait_scene(expected: String, previous_id: int = 0) -> Node:
	for i in 400:
		await process_frame
		var scene := current_scene
		if scene and scene.get_instance_id() != previous_id and scene.name == expected and scene.is_node_ready():
			await frames(4)
			room = scene
			var found = scene.get_node_or_null("CharacterBody2D")
			if found:
				player = found
			return scene
	return null

func focused() -> Control:
	return root.gui_get_focus_owner()

func focused_text() -> String:
	var control := focused()
	return control.text if control is Button else (control.name if control else "<nada>")

func title() -> Node:
	var previous := current_scene.get_instance_id() if current_scene else 0
	session.go_to_title()
	return await wait_scene("TitleScreen", previous)

func status_text(screen: Node) -> String:
	return screen.status.text

func saved() -> SaveGame.LoadResult:
	return SaveGame.load_game()

func write_raw(text: String, file := "") -> void:
	DirAccess.make_dir_recursive_absolute(DIR)
	var f := FileAccess.open(file if file else SaveGame.path(), FileAccess.WRITE)
	f.store_string(text)
	f.close()

# ---------------------------------------------------------------- pruebas

func _test_first_run_and_new_game() -> void:
	print("\n# Primera ejecución y partida nueva")
	change_scene_to_file("res://Scenes/UI/Title.tscn")
	var screen := await wait_scene("TitleScreen")
	check(screen != null and status_text(screen) == "No hay partida guardada.", "sin archivo: el título lo dice")
	check(screen.continue_button.disabled and focused_text() == "Nueva partida", "Continuar desactivado y foco en Nueva partida")
	await tap(&"ui_accept")
	var intro := await wait_scene("Intro")
	check(intro != null, "Nueva partida (sin guardado previo) va directa al plano de entrada")
	await tap(&"interact")
	await wait_scene("Atrio1")
	var result := saved()
	check(result.status == SaveGame.Status.OK and result.data.checkpoint.room_id == "atrio_1", "la partida nueva queda guardada en el inicio")
	player.inventory.from_state({"weapons": ["copper_sword", ""], "masks": ["mask_vow"]})
	session.travel("atrio_2", "checkpoint_atrio_2", player)
	await wait_scene("Atrio2", room.get_instance_id())
	await ticks(4)
	result = saved()
	check(result.status == SaveGame.Status.OK and result.data.checkpoint.spawn_id == "checkpoint_atrio_2", "encender el brasero guarda en disco")
	check(result.data.checkpoint.inventory.weapons == ["copper_sword", ""] and result.data.checkpoint.inventory.masks == ["mask_vow"], "el archivo guarda armas y máscaras por ID")
	check(not FileAccess.file_exists(SaveGame.path() + ".tmp") and FileAccess.file_exists(SaveGame.path() + ".bak"), "sin temporal colgando; la versión anterior queda como copia")

func _test_pause() -> void:
	print("\n# Pausa")
	check(session.can_pause(), "se puede pausar en una sala")
	# Mantener una dirección al pausar y soltarla durante la pausa.
	action(&"move_right", true)
	await ticks(10)
	await tap(&"pause")
	check(paused and session.pause_menu != null and focused_text() == "Reanudar", "Esc pausa y el foco empieza en Reanudar")
	var x_before := player.global_position.x
	await tap(&"attack_weapon_1")
	await frames(10)
	check(player.global_position.x == x_before and player.attack.phase == MeleeAttack.Phase.IDLE, "en pausa no se mueve ni ataca")
	action(&"move_right", false)
	await frames(2)
	# Reanudar con Espacio (también es la tecla de salto).
	await key(KEY_SPACE)
	await frames(3)
	check(not paused and session.pause_menu == null, "Reanudar con Espacio cierra la pausa")
	await ticks(20)
	check(player.is_on_floor() and absf(player.velocity.x) < 1.0, "Espacio no se convierte en salto y la tecla soltada en pausa no sigue moviendo")
	check(player.attack.phase == MeleeAttack.Phase.IDLE, "el ataque pulsado en pausa no se ejecuta después")

	# Volver al último brasero desde la pausa.
	var retries := session.retries
	await tap(&"pause")
	await tap(&"ui_down")
	check(focused_text() == "Volver al último brasero", "flecha abajo recorre el menú de pausa")
	var previous := room.get_instance_id()
	await tap(&"ui_accept")
	var back := await wait_scene("Atrio2", previous)
	check(back != null and not paused and session.retries == retries + 1, "Volver al último brasero recarga el punto sin pausa")

	# Morir y pausar durante la espera del reintento: el reintento espera.
	previous = room.get_instance_id()
	player.health.take_damage(100000.0)
	await ticks(5)
	await tap(&"pause")
	await frames(120)
	check(current_scene.get_instance_id() == previous, "con la pausa abierta el reintento por muerte no avanza")
	await tap(&"ui_cancel")
	var after := await wait_scene("Atrio2", previous)
	check(after != null, "al reanudar, el reintento se completa")

	# Durante un cambio de sala no se puede pausar.
	session.travel("atrio_3", "from_atrio_2", player)
	await frames(2)
	check(not session.can_pause(), "no se puede pausar a mitad de un cambio de sala")
	await wait_scene("Atrio3", after.get_instance_id())

func _test_title_continue_and_reopen() -> void:
	print("\n# Volver al título, continuar y reabrir")
	await tap(&"pause")
	for i in 4:
		await tap(&"ui_down")
	check(focused_text() == "Volver al título", "Volver al título es la última opción de la pausa")
	await tap(&"ui_accept")
	var screen := await wait_scene("TitleScreen")
	check(screen != null and not paused, "vuelve al título sin dejar el juego en pausa")
	check(status_text(screen).begins_with("Último brasero: Atrio del Voto"), "el título resume la partida: %s" % status_text(screen))
	check(not screen.continue_button.disabled and focused_text() == "Continuar", "Continuar disponible y con el foco")
	await tap(&"ui_accept")
	await wait_scene("Atrio2")
	check(player.global_position.distance_to(room.get_node("Spawns/checkpoint_atrio_2").global_position) < 4.0, "Continuar lleva al brasero guardado")
	check(player.inventory.to_state().masks == ["mask_vow"], "con el inventario guardado")

	# Cerrar y reabrir: se olvida todo lo que hay en memoria.
	session.run_active = false
	session.checkpoint = {}
	session.collected.clear()
	session.retries = 0
	screen = await title()
	await tap(&"ui_accept")
	await wait_scene("Atrio2")
	check(session.checkpoint.get("spawn_id") == "checkpoint_atrio_2" and session.retries > 0, "tras «reabrir» se recupera el punto y los reintentos desde disco")
	# Cargar dos veces seguidas no duplica nada.
	screen = await title()
	await tap(&"ui_accept")
	await wait_scene("Atrio2")
	check(player.inventory.carried_masks.size() == 1 and session.collected.size() == saved().data.checkpoint.collected.size(), "cargar dos veces seguidas no duplica objetos")

func _test_bad_files() -> void:
	print("\n# Archivos dañados, incompletos y de otra versión")
	var good := FileAccess.get_file_as_string(SaveGame.path())
	var cases := [
		["{\"format\": \"baldwins-curse-save\", \"version\": 1, \"checkp", "dañada", "archivo incompleto (cortado a mitad)"],
		["no es json", "dañada", "archivo con basura"],
		["{\"format\": \"baldwins-curse-save\", \"version\": 99}", "otra versión (99)", "versión desconocida"],
		[good.replace("\"atrio_2\"", "\"sala_borrada\""), "sala que ya no existe", "ID de sala que ya no existe"],
	]
	for case in cases:
		SaveGame.delete_all()
		write_raw(case[0])
		var screen := await title()
		check(status_text(screen).contains(case[1]) and screen.continue_button.disabled and focused_text() == "Nueva partida",
			"%s: «%s» y el menú sigue operativo" % [case[2], status_text(screen)])
	# ID de objeto que ya no existe: se omite y se puede continuar.
	SaveGame.delete_all()
	write_raw(good.replace("\"mask_vow\"", "\"mask_borrada\""))
	var screen := await title()
	check(not screen.continue_button.disabled and status_text(screen).contains("Se omitieron objetos"), "objeto desconocido: se avisa y se puede continuar")
	await tap(&"ui_accept")
	await wait_scene("Atrio2")
	check(player.inventory.carried_masks.is_empty() and player.inventory.get_weapon(0) != null, "se carga sin el objeto desconocido")
	# Escritura interrumpida: el principal ya pasó a .bak y el temporal no llegó.
	SaveGame.delete_all()
	write_raw(good, SaveGame.path() + ".bak")
	write_raw(good.substr(0, 40), SaveGame.path() + ".tmp")
	screen = await title()
	check(not screen.continue_button.disabled and status_text(screen).contains("copia de seguridad"), "escritura interrumpida: se recupera la copia")
	# Principal dañado con copia buena.
	SaveGame.delete_all()
	write_raw("{roto", SaveGame.path())
	write_raw(good, SaveGame.path() + ".bak")
	screen = await title()
	check(not screen.continue_button.disabled, "principal dañado y copia buena: se puede continuar")
	SaveGame.delete_all()
	write_raw(good)

func _test_completed_and_replace() -> void:
	print("\n# Partida completada y sustitución de la ranura")
	var screen := await title()
	await tap(&"ui_accept") # continuar
	await wait_scene("Atrio2")
	var previous := room.get_instance_id()
	session.finish_run()
	await wait_scene("Ending", previous)
	await tap(&"interact")
	screen = await wait_scene("TitleScreen")
	check(status_text(screen).begins_with("Partida completada") and screen.continue_button.disabled, "tras el epílogo: «%s»" % status_text(screen))
	# Nueva partida con una partida guardada: se pide confirmación, con "No" enfocado.
	await tap(&"ui_accept")
	check(focused_text() == "No, volver", "Nueva partida con guardado pide confirmación (foco en No)")
	await tap(&"ui_cancel")
	check(focused_text() == "Nueva partida" and saved().completed(), "Esc cancela, vuelve el foco y la partida sigue intacta")
	await tap(&"ui_accept")
	await tap(&"ui_down")
	await tap(&"ui_accept")
	await wait_scene("Intro")
	await tap(&"interact")
	await wait_scene("Atrio1")
	check(saved().can_continue() and saved().data.checkpoint.room_id == "atrio_1", "confirmar sustituye la ranura por la partida nueva")

func _test_settings() -> void:
	print("\n# Ajustes persistentes")
	var music := AudioServer.get_bus_index(&"Music")
	var base := AudioServer.get_bus_volume_db(music)
	GameSettings.set_volume("music", 0.5)
	check(is_equal_approx(AudioServer.get_bus_volume_db(music), base + linear_to_db(0.5)), "el volumen de música cambia el bus")
	GameSettings.set_volume("sfx", 0.0)
	check(AudioServer.is_bus_mute(AudioServer.get_bus_index(&"SFX")), "a 0 % el bus de efectos se silencia")
	GameSettings.set_reduced_effects(true)
	GameSettings.set_fullscreen(true)
	# «Reiniciar el juego»: valores por defecto en memoria y volver a leer.
	GameSettings.volumes = {"master": 1.0, "music": 1.0, "sfx": 1.0}
	GameSettings.reduced_effects = false
	GameSettings.fullscreen = false
	GameSettings.load_settings()
	check(is_equal_approx(GameSettings.volumes.music, 0.5) and GameSettings.volumes.sfx == 0.0, "los volúmenes sobreviven al reinicio")
	check(GameSettings.reduced_effects and GameSettings.fullscreen, "efectos reducidos y pantalla completa sobreviven al reinicio")
	check(is_equal_approx(GameSettings.flash_strength(), 1.3), "con efectos reducidos el destello es más suave")
	check(FileAccess.file_exists(GameSettings.path()) and GameSettings.path() != SaveGame.path(), "las preferencias van en un archivo aparte del progreso")
	write_raw("[audio]\nmusic = \"mucho\"\n", GameSettings.path())
	GameSettings.load_settings()
	check(GameSettings.volumes.music == 1.0 and not GameSettings.reduced_effects, "un archivo de ajustes dañado vuelve a los valores por defecto")
	GameSettings.set_volume("sfx", 1.0)
	GameSettings.set_fullscreen(false)

func _test_keyboard_menus() -> void:
	print("\n# Menús con teclado")
	var screen := await title()
	check(not session.can_pause(), "en el título no hay pausa")
	await tap(&"ui_down") # Nueva partida
	await tap(&"ui_down") # Ajustes
	check(focused_text() == "Ajustes", "flechas recorren el título")
	await tap(&"ui_accept")
	check(focused() is HSlider and focused().name == "Volume_master", "Ajustes abre con el foco en el primer volumen")
	var slider := focused() as HSlider
	var before := slider.value
	await tap(&"ui_left")
	check(slider.value == before - 5.0 and is_equal_approx(GameSettings.volumes.master, (before - 5.0) / 100.0), "flecha izquierda baja el volumen y se guarda")
	await tap(&"ui_right")
	await tap(&"ui_cancel")
	check(focused_text() == "Ajustes", "Esc cierra Ajustes y devuelve el foco")
	await tap(&"ui_down")
	await tap(&"ui_accept")
	var labels := []
	for node in screen.find_children("*", "Label", true, false):
		labels.append(node.text)
	check(labels.has("Espacio / Arriba") and labels.has("Esc / P"), "Controles muestra las teclas del InputMap en español")
	await tap(&"ui_cancel")
	check(focused_text() == "Controles", "y vuelve al menú")
	await tap(&"ui_down")
	await tap(&"ui_accept")
	var credits := false
	for node in screen.find_children("*", "Label", true, false):
		credits = credits or node.text.contains("DA0806")
	check(credits, "Créditos nombra al autor original")
	await tap(&"ui_cancel")
	await tap(&"ui_cancel")
	check(current_scene == screen and focused_text() == "Créditos", "Esc en el menú principal no lo cierra")
