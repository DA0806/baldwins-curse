extends SceneTree
## Verificaciones de la etapa 4 (sala de referencia del Atrio). Lo visual se
## revisa con capturas (tools/stage4_capture.gd); aquí va lo que se puede medir.
##
##   godot --headless --fixed-fps 60 --path . -s res://Tests/stage4_tests.gd

const AMBIENCE := "res://Audio/amb_atrio.wav"
const P := MeleeAttack.Phase

var session: RunSession
var player: CharacterBody2D
var checks := 0
var failures := 0

func _initialize() -> void:
	_run()

func _run() -> void:
	await process_frame
	SaveGame.directory = "user://tests/"
	session = root.get_node_or_null("GameSession") as RunSession
	if not session:
		session = (load("res://Scripts/GameSession.gd") as GDScript).new()
		session.name = "GameSession"
		root.add_child(session)
	_test_static()
	await _test_room()
	print("\n== %d comprobaciones, %d fallas ==" % [checks, failures])
	quit(1 if failures > 0 else 0)

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures += 1
	print("  %s %s" % ["ok  " if condition else "FAIL", message])

func ticks(count: int) -> void:
	for i in count:
		await physics_frame

func wait_scene(expected: String, previous_id: int = 0) -> Node:
	for i in 300:
		await process_frame
		var scene := current_scene
		if scene and scene.get_instance_id() != previous_id and scene.name == expected and scene.is_node_ready():
			await ticks(3)
			player = scene.get_node("CharacterBody2D")
			return scene
	return null

func _test_static() -> void:
	print("\n# Proyecto, tema y jugador")
	var theme_path: String = ProjectSettings.get_setting("gui/theme/custom", "")
	var theme := load(theme_path) as Theme if theme_path else null
	check(theme != null and theme.has_color(&"font_color", &"Label"), "tema de interfaz del proyecto cargado")
	var missing := ""
	for glyph in "áéíóúüñÁÉÍÓÚÑ¿¡«»—·":
		if not ThemeDB.fallback_font.has_char(glyph.unicode_at(0)):
			missing += glyph
	check(missing.is_empty(), "la fuente cubre los glifos del español%s" % ("" if missing.is_empty() else " (faltan %s)" % missing))
	check(AudioServer.get_bus_index(&"Music") > 0 and AudioServer.get_bus_index(&"SFX") > 0, "buses Music y SFX")
	check(not Hitbox.debug_draw, "las zonas de golpe no se dibujan por defecto (F3)")
	var scene := (load("res://Scenes/player.tscn") as PackedScene).instantiate()
	var shape: CollisionShape2D = scene.get_node("CollisionShape2D")
	var left: RayCast2D = scene.get_node("RayLeft")
	var right: RayCast2D = scene.get_node("RayRight")
	check(shape.position.x == 0.0 and left.position.x == -right.position.x, "colisionador y rayos simétricos respecto al pivote")
	scene.free()

func _test_room() -> void:
	print("\n# Atrio 2 (sala de referencia)")
	session.new_run()
	var room := await wait_scene("Atrio1")
	check(session.current_ambience() == load(AMBIENCE), "el Atrio 1 suena con el ambiente del Atrio")
	player.inventory.from_state({"weapons": ["copper_sword", ""], "masks": ["mask_vow"]})
	var fade: ColorRect = session._fade_rect
	session.travel("atrio_2", "from_atrio_1", player)
	await ticks(8)
	check(fade.color.a > 0.3 and current_scene == room, "la salida funde a negro antes de cambiar de sala")
	room = await wait_scene("Atrio2", room.get_instance_id())
	check(room != null, "llega al Atrio 2")
	check(session.current_ambience() == load(AMBIENCE), "entra el ambiente del Atrio")
	await ticks(30)
	check(fade.color.a < 0.05, "el fundido se aclara al llegar")

	var geometry = room.get_node("Geometry")
	check(geometry.fill_texture != null and geometry.top_texture != null, "suelo con tiles de 16 px")
	for rect: Rect2 in geometry.blocks:
		if int(rect.position.x) % 16 != 0 or int(rect.position.y) % 16 != 0 or int(rect.size.x) % 16 != 0:
			check(false, "bloque fuera de la cuadrícula de 16 px: %s" % rect)

	var brazier: Sprite2D = room.get_node("Spawns/checkpoint_atrio_2/Art")
	check(brazier.frame == 0, "brasero apagado antes de tocarlo")
	player.respawn_at(Vector2(150, 224))
	await ticks(6)
	await process_frame
	check(brazier.frame >= 1, "brasero encendido al activarlo")

	var enemy = room.get_node("GroundEnemy")
	var art: Sprite2D = enemy.get_node("Art")
	var definition: Dictionary = enemy._presentation.definition
	var initial_clip: String = enemy._presentation.current_clip
	var initial_sequence: Dictionary = definition.clips[initial_clip]
	check(not enemy.body.visible and initial_clip in ["Idle", "Walk"]
		and art.frame >= initial_sequence.start and art.frame < initial_sequence.start + initial_sequence.count,
		"custodio usa su secuencia de reposo o patrulla")
	player.respawn_at(enemy.global_position + Vector2(-30, -8))
	var seen := {}
	var startup_frames := {}
	for i in 240:
		await physics_frame
		seen[enemy.attack.phase] = art.frame
		if enemy.attack.phase == P.STARTUP:
			startup_frames[art.frame] = true
		if seen.has(P.RECOVERY):
			break
	var phase_ranges := {P.STARTUP: "Startup", P.ACTIVE: "Active", P.RECOVERY: "Recovery"}
	var correct_ranges := true
	for phase in phase_ranges:
		var sequence: Dictionary = definition.clips[phase_ranges[phase]]
		var sampled: int = seen.get(phase, -1)
		correct_ranges = correct_ranges and sampled >= sequence.start and sampled < sequence.start + sequence.count
	check(correct_ranges, "cada fase usa su secuencia propia, sincronizada con el combate (%s)" % seen)
	check(startup_frames.size() > 1, "anticipación avanza por varios cuadros antes del daño")
	check(art.flip_h, "mira al jugador (a su izquierda)")

	player.health.reset()
	session.travel("atrio_3", "from_atrio_2", player)
	room = await wait_scene("Atrio3", room.get_instance_id())
	check(room != null and session.current_ambience() == load(AMBIENCE), "dentro del Atrio el ambiente sigue sin cortes")
	session.travel("cripta_1", "from_atrio_3", player)
	room = await wait_scene("Cripta1", room.get_instance_id())
	check(room != null and session.current_ambience() == load("res://Audio/amb_cripta.wav"), "al entrar en la Cripta cambia al ambiente de la Cripta")
