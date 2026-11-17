extends SceneTree
## Verificaciones de la etapa 5 (campaña, enemigo a distancia, jefe y epílogo).
##
##   godot --headless --fixed-fps 60 --path . -s res://Tests/stage5_tests.gd
##
## El jefe lo vence un jugador simulado que sólo pulsa acciones del InputMap y
## lee lo mismo que vería una persona: el estado visible del Abad (pose de
## anticipación, marcas de brasa en el suelo, sello encendido).

const P := MeleeAttack.Phase
const ORDER := ["atrio_1", "atrio_2", "atrio_3", "cripta_1", "cripta_2", "cripta_3", "cripta_4", "capilla_1", "capilla_2", "capilla_3"]
const MAX_GAP := 96.0  # hueco máximo saltable con margen (alcance medido: 129 px)
const MAX_STEP := 64.0 # escalón máximo (altura medida del salto: 77 px)

var session: RunSession
var player: CharacterBody2D
var inv: PlayerInventory
var room: Node
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
	_test_route_contract()
	await _test_full_route()
	await _test_checkpoints()
	await _test_acolyte()
	await _test_boss_patterns()
	for combo in [["copper_sword", "mask_vow"], ["copper_sword", "mask_ember"], ["crypt_mace", "mask_vow"], ["crypt_mace", "mask_ember"]]:
		await _test_boss_fight(combo[0], combo[1])
	await _test_boss_retry()
	print("\n== %d comprobaciones, %d fallas ==" % [checks, failures])
	quit(1 if failures > 0 else 0)

# ---------------------------------------------------------------- utilidades

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures += 1
	print("  %s %s" % ["ok  " if condition else "FAIL", message])

func ticks(count: int) -> void:
	for i in count:
		await physics_frame

func press(action: StringName, pressed: bool) -> void:
	if Input.is_action_pressed(action) == pressed:
		return
	var event := InputEventAction.new()
	event.action = action
	event.pressed = pressed
	Input.parse_input_event(event)

func tap(action: StringName) -> void:
	press(action, true)
	await ticks(2)
	press(action, false)
	await ticks(1)

func release_all() -> void:
	for action in [&"move_left", &"move_right", &"jump"]:
		press(action, false)

func wait_scene(expected: String, previous_id: int = 0) -> Node:
	for i in 400:
		await process_frame
		var scene := current_scene
		if scene and scene.get_instance_id() != previous_id and scene.name == expected and scene.is_node_ready():
			await ticks(3)
			room = scene
			var found = scene.get_node_or_null("CharacterBody2D")
			if found:
				player = found
				inv = player.inventory
			return scene
	return null

func scene_name(room_id: String) -> String:
	return String(session.ROOMS[room_id]).get_file().get_basename()

## Lleva el estado actual a una sala (como una salida) y espera a que cargue.
func go(room_id: String, spawn_id: String, state: Dictionary = {}) -> Node:
	var previous := current_scene.get_instance_id() if current_scene else 0
	if not state.is_empty():
		inv.from_state(state)
	release_all()
	session.travel(room_id, spawn_id, player)
	return await wait_scene(scene_name(room_id), previous)

func place(at: Vector2, settle: int = 4) -> void:
	player.respawn_at(at)
	await ticks(settle)

# ---------------------------------------------------------------- contrato

func _test_route_contract() -> void:
	print("\n# Contrato de la ruta (10 salas)")
	check(session.ROOMS.keys() == ORDER, "diez salas en el orden de docs/etapa5/ruta.md")
	var checkpoints := []
	var uniques := []
	var inscriptions := 0
	var ends := []
	var problems := []
	for room_id in ORDER:
		var scene: Node = (load(session.ROOMS[room_id]) as PackedScene).instantiate()
		if scene.room_id != room_id:
			problems.append("%s: room_id %s" % [room_id, scene.room_id])
		var spawns: Node = scene.get_node_or_null("Spawns")
		for child in (spawns.get_children() if spawns else []):
			if child.get_script() and String(child.get_script().resource_path).ends_with("Checkpoint.gd"):
				checkpoints.append(child.name)
		for node in scene.find_children("*", "", true, false):
			if node.get("unique_id") is String and not String(node.get("unique_id")).is_empty():
				uniques.append(node.unique_id)
			if node.get_script() and String(node.get_script().resource_path).ends_with("Inscription.gd"):
				inscriptions += 1
		var exit: Node = scene.get_node_or_null("Exit")
		if not exit:
			problems.append("%s sin salida" % room_id)
		elif exit.ends_run:
			ends.append(room_id)
		else:
			var target: Node = (load(session.ROOMS[exit.target_room]) as PackedScene).instantiate()
			if not target.has_node("Spawns/" + exit.target_spawn):
				problems.append("%s -> %s/%s no existe" % [room_id, exit.target_room, exit.target_spawn])
			if ORDER.find(exit.target_room) != ORDER.find(room_id) + 1:
				problems.append("%s no lleva a la sala siguiente" % room_id)
			target.free()
		problems.append_array(_geometry_problems(room_id, scene.get_node("Geometry").blocks))
		scene.free()
	check(problems.is_empty(), "salidas, llegadas y room_id coherentes; huecos ≤ 96 px y escalones ≤ 64 px %s" % [problems])
	check(checkpoints.size() == 5 and checkpoints.size() == _unique_count(checkpoints), "cinco puntos de control con ID único: %s" % [checkpoints])
	check(uniques.size() == _unique_count(uniques), "recogidas únicas sin IDs repetidos (%d)" % uniques.size())
	check(inscriptions == 3, "tres inscripciones (%d)" % inscriptions)
	check(ends == ["capilla_3"], "sólo la arena del jefe termina la partida")

func _unique_count(list: Array) -> int:
	var seen := {}
	for item in list:
		seen[item] = true
	return seen.size()

## Suelo a y=256: huecos entre tramos y altura de bloques elevados.
func _geometry_problems(room_id: String, blocks: Array) -> Array:
	var problems := []
	var floors := blocks.filter(func(r: Rect2): return r.position.y == 256.0)
	floors.sort_custom(func(a: Rect2, b: Rect2): return a.position.x < b.position.x)
	for i in range(1, floors.size()):
		var gap: float = floors[i].position.x - floors[i - 1].end.x
		if gap > MAX_GAP:
			problems.append("%s: hueco de %d px" % [room_id, gap])
	for r: Rect2 in blocks:
		if r.end.y == 256.0 and r.position.y > 0.0 and 256.0 - r.position.y > MAX_STEP:
			problems.append("%s: escalón de %d px" % [room_id, 256.0 - r.position.y])
	return problems

# ---------------------------------------------------------------- recorrido

func _test_full_route() -> void:
	print("\n# Recorrido completo de inicio a epílogo")
	session.start_campaign()
	var intro := await wait_scene("Intro")
	check(intro != null and intro.get_node("Story").text.contains("Baldwin"), "plano de entrada con la motivación de Baldwin")
	await tap(&"interact")
	await wait_scene("Atrio1")
	var pickups := {"atrio_1": "Sword", "atrio_2": "MaskVow", "cripta_1": "MaskEmber", "cripta_2": "Mace"}
	var visited := []
	var final_state := {}
	for room_id in ORDER:
		visited.append(room.room_id)
		if pickups.has(room_id):
			var pickup: Node2D = room.get_node(pickups[room_id])
			await place(pickup.global_position + Vector2(0, 12))
			player.try_interact()
		var encounter := room.get_node_or_null("Encounter")
		if encounter:
			for enemy in encounter.get_children():
				if enemy.has_node("Health"):
					enemy.get_node("Health").take_damage(100000.0)
			await ticks(3)
			if not encounter.is_cleared() or room.has_node("Gate"):
				check(false, "%s: el encuentro no abre la reja" % room_id)
		var previous := room.get_instance_id()
		var exit: Node2D = room.get_node("Exit")
		player.health.reset()
		final_state = inv.to_state()
		await place(exit.global_position + Vector2(0, 16), 1)
		if room_id == "capilla_3":
			var ending := await wait_scene("Ending", previous)
			check(ending != null and session.finished, "la salida tras el Abad lleva al epílogo")
			check(ending != null and ending.get_node("Body").text.contains("sello"), "el epílogo cierra la historia")
		else:
			var next := await wait_scene(scene_name(ORDER[ORDER.find(room_id) + 1]), previous)
			if not next:
				check(false, "%s: la salida no lleva a la sala siguiente" % room_id)
				return
	check(visited == ORDER, "recorre las diez salas en orden")
	check(final_state.get("weapons") == ["copper_sword", "crypt_mace"], "llega con espada y maza")
	check(final_state.get("masks") == ["mask_vow", "mask_ember"], "llega con Voto y Ascua")

func _test_checkpoints() -> void:
	print("\n# Reintento desde cada punto de control")
	session.new_run()
	await wait_scene("Atrio1")
	var points := {"atrio_2": "checkpoint_atrio_2", "atrio_3": "checkpoint_atrio_3", "cripta_1": "checkpoint_cripta_1",
		"cripta_3": "checkpoint_cripta_3", "capilla_2": "checkpoint_capilla_2"}
	var state := {"weapons": ["copper_sword", "crypt_mace"], "masks": ["mask_vow", "mask_ember"]}
	for room_id in points:
		await go(room_id, points[room_id], state)
		var marker_position: Vector2 = (room.get_node("Spawns/" + points[room_id]) as Node2D).global_position
		await ticks(3)
		var active := session.is_active_checkpoint(room_id, points[room_id])
		var retries := session.retries
		var previous := room.get_instance_id()
		player.health.take_damage(100000.0)
		var reloaded := await wait_scene(scene_name(room_id), previous)
		var ok: bool = reloaded != null and active and session.retries == retries + 1 \
			and player.global_position.distance_to(marker_position) < 4.0 and inv.carried_masks.size() == 2
		check(ok, "%s: muerte -> reaparece en %s con su equipo" % [room_id, points[room_id]])

# ---------------------------------------------------------------- acólito

func _test_acolyte() -> void:
	print("\n# Acólito de la Ascua (enemigo a distancia)")
	await go("cripta_3", "checkpoint_cripta_3", {"weapons": ["copper_sword", ""], "masks": []})
	var acolyte = room.get_node("Acolyte")
	await place(Vector2(acolyte.global_position.x - 200, 224))
	var orb: EmberOrb = await _next_orb(acolyte)
	check(orb != null, "anticipa (con \"!\") y lanza una brasa")
	var before: float = player.health.current
	for i in 180:
		if not is_instance_valid(orb):
			break
		await physics_frame
	check(is_equal_approx(before - player.health.current, 12.0), "la brasa quita 12 sin máscara (%.1f)" % (before - player.health.current))

	player.health.reset()
	inv.from_state({"weapons": ["copper_sword", ""], "masks": ["mask_vow"]})
	await ticks(60)
	orb = await _next_orb(acolyte)
	before = player.health.current
	for i in 180:
		if not is_instance_valid(orb):
			break
		await physics_frame
	check(is_equal_approx(before - player.health.current, 9.6), "con Voto quita 9,6")

	# Saltarla: se pulsa salto cuando está a 70 px.
	player.health.reset()
	await ticks(60)
	orb = await _next_orb(acolyte)
	before = player.health.current
	for i in 240:
		if not is_instance_valid(orb):
			break
		if absf(orb.global_position.x - player.global_position.x) < 70.0 and player.is_on_floor():
			press(&"jump", true)
		await physics_frame
	press(&"jump", false)
	await ticks(40)
	check(player.health.current == before, "saltar a tiempo la esquiva")

	# Cubrirse tras la lápida (x 592-640): la brasa choca y se apaga.
	player.health.reset()
	await place(Vector2(570, 224), 30)
	before = player.health.current
	orb = await _next_orb(acolyte)
	var died_at := 0.0
	for i in 240:
		if not is_instance_valid(orb):
			break
		died_at = orb.global_position.x
		await physics_frame
	check(player.health.current == before and died_at > 600.0, "la lápida detiene la brasa (se apagó en x %.0f)" % died_at)

func _next_orb(acolyte) -> EmberOrb:
	var got := []
	var grab := func(o): got.append(o)
	acolyte.threw.connect(grab)
	for i in 300:
		if not got.is_empty():
			break
		await physics_frame
	acolyte.threw.disconnect(grab)
	return got[0] if not got.is_empty() else null

# ---------------------------------------------------------------- jefe

func _enter_arena(weapon: String, mask: String) -> Boss:
	session.new_run()
	await wait_scene("Atrio1")
	await go("capilla_3", "from_capilla_2", {"weapons": [weapon, ""], "masks": [mask]})
	return room.get_node("Encounter/Abbot") as Boss

func _test_boss_patterns() -> void:
	print("\n# Abad Sellado: patrones, ventanas y fase 2")
	var boss := await _enter_arena("copper_sword", "mask_vow")
	check(boss.state == Boss.State.DORMANT and not boss.bar_layer.visible, "dormido hasta que Baldwin se acerca")
	await place(Vector2(boss.global_position.x - 250, 224))
	await ticks(5)
	check(boss.state == Boss.State.STAGGER and boss.bar_layer.visible, "despierta con un rugido y muestra su barra")

	var log := {}
	boss.pattern_started.connect(func(p): log[p] = log.get(p, 0) + 1)
	var invulnerable_hits := [0]
	var vulnerable_hits := [0]
	var state_ticks := {}
	for i in 900:
		await physics_frame
		state_ticks[boss.state] = state_ticks.get(boss.state, 0) + 1
		# Golpes directos a la zona vulnerable: sólo cuentan si está encendida.
		if i % 20 == 0 and boss.state != Boss.State.DEAD:
			var landed: float = boss.hurtbox.receive_hit(0.01, player) if boss.hurtbox.monitorable else 0.0
			if boss.vulnerable and landed > 0.0:
				vulnerable_hits[0] += 1
			elif not boss.vulnerable and boss.hurtbox.monitorable and boss.state in [Boss.State.ADVANCE, Boss.State.SWEEP_TELL, Boss.State.RAIN_TELL]:
				invulnerable_hits[0] += 1
		player.health.reset()
		if log.get(&"rain", 0) >= 1 and state_ticks.get(Boss.State.EXHAUSTED, 0) > 0 and boss.state == Boss.State.ADVANCE:
			break
	check(log.get(&"sweep", 0) >= 1 and log.get(&"rain", 0) >= 1, "usa los dos patrones: %s" % [log])
	check(absi(state_ticks.get(Boss.State.SWEEP_TELL, 0) - 48) <= 2, "anticipación del tajo de 0,8 s (%d ticks)" % state_ticks.get(Boss.State.SWEEP_TELL, 0))
	check(absi(state_ticks.get(Boss.State.RAIN_TELL, 0) - 54) <= 2, "anticipación de la lluvia de 0,9 s (%d ticks)" % state_ticks.get(Boss.State.RAIN_TELL, 0))
	check(boss.rain_targets.size() == 3 and is_equal_approx(boss.rain_targets[1] - boss.rain_targets[0], 80.0), "lluvia de 3 brasas a 80 px")
	check(state_ticks.get(Boss.State.SWEEP_RECOVER, 0) > 0 and state_ticks.get(Boss.State.EXHAUSTED, 0) > 0, "ventanas de castigo tras cada patrón")
	check(invulnerable_hits[0] == 0, "su zona vulnerable está apagada fuera de las ventanas")
	check(vulnerable_hits[0] > 0, "y encendida durante ellas")

	var phases := []
	boss.phase_changed.connect(func(p): phases.append(p))
	boss.health.take_damage(boss.health.current - boss.health.max_health * 0.5 + 1.0)
	boss.health.take_damage(2.0)
	await ticks(2)
	check(phases == [2] and boss.state == Boss.State.STAGGER and not boss.vulnerable, "a la mitad ruge (1,2 s sin daño) y pasa a la fase 2")
	check(is_equal_approx(boss.tell(boss.sweep_tell), 0.6) and is_equal_approx(boss.tell(boss.rain_tell), 0.675), "fase 2: anticipaciones un 25 % más cortas")
	var seen := []
	boss.pattern_started.connect(func(p): seen.append(p))
	for i in 1200:
		await physics_frame
		player.health.reset()
		if seen.size() >= 3 and boss.state == Boss.State.RAIN_TELL:
			break
	check(seen.slice(0, 3) == [&"sweep", &"sweep", &"rain"], "fase 2: dos tajos por cada lluvia (%s)" % [seen])
	check(boss.rain_targets.size() == 5 and is_equal_approx(boss.rain_targets[1] - boss.rain_targets[0], 64.0), "fase 2: lluvia de 5 brasas a 64 px")

## Jugador simulado: salta el tajo al final de su anticipación, se coloca entre
## dos marcas de brasa durante la lluvia y ataca sólo con el sello encendido.
func _test_boss_fight(weapon: String, mask: String) -> void:
	print("\n# Combate completo: %s + %s" % [weapon, mask])
	var boss := await _enter_arena(weapon, mask)
	await place(Vector2(boss.global_position.x - 200, 224))
	var hits_taken := [0]
	player.health.damaged.connect(func(_a, _s): hits_taken[0] += 1)
	var start := Engine.get_physics_frames()
	var won := false
	for i in 60 * 120:
		if boss.state == Boss.State.DEAD:
			won = true
			break
		if player.health.is_dead():
			break
		await _bot_step(boss)
	release_all()
	var seconds := (Engine.get_physics_frames() - start) / 60.0
	check(won and not player.health.is_dead(), "vence al Abad en %.0f s (salud final %d, golpes recibidos %d)" % [seconds, player.health.current, hits_taken[0]])
	await ticks(3)
	check(room.get_node_or_null("Gate") == null, "al caer el Abad se abre la salida")

func _bot_step(boss: Boss) -> void:
	var dx: float = boss.global_position.x - player.global_position.x
	match boss.state:
		Boss.State.SWEEP_TELL, Boss.State.SWEEP:
			press(&"move_left", false)
			press(&"move_right", false)
			if boss.state == Boss.State.SWEEP_TELL and boss.attack._phase_left <= 0.1 and player.is_on_floor():
				press(&"jump", true)
		Boss.State.SWEEP_RECOVER, Boss.State.EXHAUSTED:
			press(&"jump", false)
			await _approach_and_strike(dx)
		Boss.State.RAIN_TELL, Boss.State.RAIN:
			press(&"jump", false)
			var targets := boss.rain_targets.duplicate()
			targets.sort()
			var best := player.global_position.x
			var best_dist := INF
			for i in range(1, targets.size()):
				var mid: float = (targets[i - 1] + targets[i]) / 2.0
				if absf(mid - player.global_position.x) < best_dist:
					best = mid
					best_dist = absf(mid - player.global_position.x)
			var to_go: float = best - player.global_position.x
			press(&"move_right", to_go > 3.0)
			press(&"move_left", to_go < -3.0)
		_:
			press(&"jump", false)
			press(&"move_left", false)
			press(&"move_right", false)
	await physics_frame

func _approach_and_strike(dx: float) -> void:
	var reach: float = inv.get_weapon(0).reach
	if absf(dx) > reach - 14.0:
		press(&"move_right", dx > 0.0)
		press(&"move_left", dx < 0.0)
		return
	press(&"move_right", false)
	press(&"move_left", false)
	# Mirar al Abad antes de golpear.
	if (dx > 0.0) == player.sprite.flip_h:
		await tap(&"move_right" if dx > 0.0 else &"move_left")
	if player.attack.can_start():
		await tap(&"attack_weapon_1")

func _test_boss_retry() -> void:
	print("\n# Morir ante el Abad y repetir")
	session.new_run()
	await wait_scene("Atrio1")
	await go("capilla_2", "checkpoint_capilla_2", {"weapons": ["copper_sword", ""], "masks": ["mask_vow"]})
	await ticks(3)
	room = await go("capilla_3", "from_capilla_2")
	var boss: Boss = room.get_node("Encounter/Abbot")
	boss.health.take_damage(120.0)
	var previous := room.get_instance_id()
	player.health.take_damage(100000.0)
	var back := await wait_scene("Capilla2", previous)
	check(back != null and session.is_active_checkpoint("capilla_2", "checkpoint_capilla_2"), "vuelve al brasero de la antesala")
	room = await go("capilla_3", "from_capilla_2")
	boss = room.get_node("Encounter/Abbot")
	check(boss.health.current == boss.health.max_health and boss.state == Boss.State.DORMANT, "el Abad vuelve entero y dormido")
