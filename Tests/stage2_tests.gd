extends SceneTree
## Verificaciones de la etapa 2 (combate, daño, muerte, reintento y enemigo).
##
##   godot --headless --fixed-fps 60 --path . -s res://Tests/stage2_tests.gd
##
## Termina con código 0 si todo pasa y 1 si algo falla.

const WORLD_SCENE := "res://Scenes/world.tscn"
const DUMMY_SCENE := "res://Scenes/Enemies/TrainingDummy.tscn"
const SWORD := "res://Items/Weapons/Copper_Sword_test.tres"
const MACE := "res://Items/Weapons/Test_Mace.tres"
const TICK := 1.0 / 60.0
const FLOOR_Y := 224.0 # y del jugador apoyado en el suelo
const DUMMY_Y := 232.0 # y de un cuerpo de 48 px apoyado en el suelo
const P := MeleeAttack.Phase

var world: Node2D
var player: CharacterBody2D
var inv: PlayerInventory
var hud: InventoryHUD
var sword: WeaponData
var mace: WeaponData
var checks := 0
var failures := 0
## Cambios de fase del ataque del jugador: [fase, tick de física].
var phases: Array = []
var active_rect := Rect2()
var active_frame := -1
var active_clip: StringName = &""

func _initialize() -> void:
	_run()

func _run() -> void:
	await process_frame # el árbol aún no ha arrancado dentro de _initialize
	sword = load(SWORD)
	mace = load(MACE)
	await _test_weapons_and_empty_slot()
	await _test_hits_and_damage()
	await _test_reach_and_mirror()
	await _test_window_and_duplicates()
	await _test_input_repeat()
	await _test_interruption_and_death()
	await _test_enemy()
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

func send(action: StringName, pressed: bool) -> void:
	var event := InputEventAction.new()
	event.action = action
	event.pressed = pressed
	Input.parse_input_event(event)

func tap(action: StringName) -> void:
	send(action, true)
	await ticks(2)
	send(action, false)
	await ticks(1)

## Carga la sala. Con `arena` se quitan el enemigo y el maniquí de la escena
## para probar el combate del jugador con maniquíes colocados a medida.
func load_world(arena: bool) -> void:
	for action in [&"move_left", &"move_right", &"jump"]:
		Input.action_release(action)
	if world:
		world.queue_free()
		await ticks(2)
	world = (load(WORLD_SCENE) as PackedScene).instantiate()
	root.add_child(world)
	current_scene = world
	player = world.get_node("CharacterBody2D")
	inv = player.inventory
	hud = world.get_node("InventoryHUD")
	if arena:
		world.get_node("GroundEnemy").free()
		world.get_node("TrainingDummy").free()
	phases.clear()
	player.attack.phase_changed.connect(_on_player_phase)
	await ticks(10)

func _on_player_phase(phase: int) -> void:
	phases.append([phase, Engine.get_physics_frames()])
	if phase == P.ACTIVE:
		active_rect = player.attack.hitbox.get_world_rect()
		active_frame = player.sprite.frame
		active_clip = player.sprite.animation

func attack_starts() -> int:
	return phases.filter(func(entry): return entry[0] == P.STARTUP).size()

func last_start_frame() -> int:
	for i in range(phases.size() - 1, -1, -1):
		if phases[i][0] == P.STARTUP:
			return phases[i][1]
	return -1

func wait_phase(phase: int, limit: int = 120) -> bool:
	for i in limit:
		if player.attack.phase == phase:
			return true
		await physics_frame
	return false

## Deja al jugador quieto en x, mirando hacia `dir`, con el ataque disponible.
func stand(x: float, dir: int = 1) -> void:
	Input.action_press(&"move_right" if dir == 1 else &"move_left")
	await ticks(3)
	Input.action_release(&"move_right")
	Input.action_release(&"move_left")
	await ticks(12)
	player.respawn_at(Vector2(x, FLOOR_Y))
	player.attack.cooldown_left = 0.0
	await ticks(6)

func spawn_dummy(x: float) -> TrainingDummy:
	var dummy := (load(DUMMY_SCENE) as PackedScene).instantiate() as TrainingDummy
	dummy.position = Vector2(x, DUMMY_Y)
	world.add_child(dummy)
	await ticks(3)
	return dummy

func clear_dummies() -> void:
	for node in world.get_children():
		if node is TrainingDummy:
			node.free()
	await ticks(2)

func any_hitbox_active() -> bool:
	for hitbox in get_nodes_in_group(Hitbox.GROUP):
		if hitbox.active:
			return true
	return false

# --------------------------------------------------------------------- armas

func _test_weapons_and_empty_slot() -> void:
	print("\n[armas] datos y ranura vacía")
	check(sword.id == "copper_sword" and mace.id == "test_mace", "las dos armas tienen IDs estables")
	check(sword.base_damage != mace.base_damage and sword.reach != mace.reach and sword.recovery != mace.recovery,
		"daño, alcance y recuperación distinguibles (espada %d/%d px/%.2f s · maza %d/%d px/%.2f s)" % [
			sword.base_damage, sword.reach, sword.recovery, mace.base_damage, mace.reach, mace.recovery])
	await load_world(true)
	var dummy := await spawn_dummy(360)
	await stand(320)
	await tap(&"attack_weapon_1")
	await tap(&"attack_weapon_2")
	await ticks(20)
	check(attack_starts() == 0 and player.current_state != player.State.ATTACK and not String(player.sprite.animation).begins_with("Attack"),
		"ranura vacía: ni ataque ni animación de ataque")
	check(dummy.hit_log.is_empty(), "ranura vacía: cero daño")

func _test_hits_and_damage() -> void:
	print("\n[golpe] daño exacto por arma y tiempos")
	await load_world(true)
	inv.equip_weapon(0, sword)
	inv.equip_weapon(1, mace)
	var dummy := await spawn_dummy(360)
	await stand(320)

	await tap(&"attack_weapon_1")
	check(player.current_state == player.State.ATTACK and player.sprite.animation == &"AttackSwordStartup", "Z con espada: ataque y animación")
	await ticks(40)
	check(dummy.hit_log.size() == 1 and dummy.hit_log[0].damage == 20.0, "la espada golpea una vez por 20")
	check(dummy.health.current == dummy.health.max_health - 20.0, "la salud del objetivo baja exactamente 20")
	var delay: int = dummy.hit_log[0].frame - last_start_frame()
	check(delay >= floori(sword.startup / TICK) and delay <= ceili((sword.startup + sword.active_time) / TICK) + 1,
		"el golpe cae dentro de la ventana activa (%d ticks tras aceptar el ataque)" % delay)
	check(active_clip == &"AttackSwordActive" and active_frame == 0, "la ventana de daño inicia el clip activo de espada desde su primer cuadro")
	check(inv.active_weapon_slot == 0, "atacar con Z deja la ranura 1 como ranura de intercambio")

	await tap(&"attack_weapon_2")
	await ticks(60)
	check(dummy.hit_log.size() == 2 and dummy.hit_log[1].damage == 35.0, "la maza golpea una vez por 35")
	delay = dummy.hit_log[1].frame - last_start_frame()
	check(delay >= floori(mace.startup / TICK) and delay <= ceili((mace.startup + mace.active_time) / TICK) + 1,
		"la maza tarda más en golpear (%d ticks)" % delay)
	check(active_clip == &"AttackMaceActive" and active_frame == 0, "la maza inicia su propio clip activo con la misma autoridad de daño")
	check(inv.active_weapon_slot == 1 and hud.weapon_key_labels[1].text == "[X]", "atacar con X mueve la ranura de intercambio y el HUD lo muestra")
	check(player.current_state != player.State.ATTACK and not any_hitbox_active(), "al terminar no queda zona de golpe abierta")

func _test_reach_and_mirror() -> void:
	print("\n[golpe] alcance, espalda y espejo")
	await load_world(true)
	inv.equip_weapon(0, sword)
	var rects := {}
	for dir in [1, -1]:
		var side: String = "derecha" if dir == 1 else "izquierda"
		# La espada llega a 60 px; el maniquí mide 24 px de ancho.
		for case in [[68.0, true, "dentro del alcance"], [76.0, false, "fuera del alcance"], [-40.0, false, "detrás del atacante"]]:
			await clear_dummies()
			var dummy := await spawn_dummy(320.0 + dir * case[0])
			await stand(320, dir)
			await tap(&"attack_weapon_1")
			await ticks(40)
			var was_hit: bool = dummy.hit_log.size() == 1
			check(was_hit == case[1] and dummy.hit_log.size() <= 1, "%s, objetivo %s: %s" % [
				side, case[2], "recibe 20" if case[1] else "conserva su salud"])
		rects[dir] = Rect2(active_rect.position - Vector2(320, FLOOR_Y), active_rect.size)
	check(rects[1].position.x == 6.0 and rects[1].end.x == 60.0, "zona de golpe a la derecha: de +6 a +60 px")
	check(rects[-1].position.x == -60.0 and rects[-1].end.x == -6.0, "zona de golpe a la izquierda: de -60 a -6 px (espejo exacto)")

func _test_window_and_duplicates() -> void:
	print("\n[golpe] ventana activa y duplicados")
	await load_world(true)
	inv.equip_weapon(0, sword)

	# Un objetivo que sólo es vulnerable después de la ventana activa.
	var late := await spawn_dummy(360)
	var late_hurtbox: Hurtbox = late.get_node("Hurtbox")
	late_hurtbox.set_enabled(false)
	await stand(320)
	await tap(&"attack_weapon_1")
	await wait_phase(P.RECOVERY)
	check(player.attack.phase == P.RECOVERY and not player.attack.hitbox.active, "en la recuperación la zona de golpe está cerrada")
	late_hurtbox.set_enabled(true)
	await ticks(40)
	check(late.hit_log.is_empty(), "un objetivo que aparece fuera de la ventana conserva su salud")

	# Un objetivo con dos zonas vulnerables solapadas.
	await clear_dummies()
	var twin := await spawn_dummy(360)
	var extra: Hurtbox = twin.get_node("Hurtbox").duplicate()
	extra.position.x = 6.0
	twin.add_child(extra)
	extra.health = twin.health
	await stand(320)
	await tap(&"attack_weapon_1")
	await ticks(40)
	check(twin.hit_log.size() == 1 and twin.health.current == twin.health.max_health - 20.0,
		"dos zonas vulnerables del mismo objetivo: un solo golpe")

	# Dos objetivos distintos dentro de la zona.
	await clear_dummies()
	var near_dummy := await spawn_dummy(350)
	var far_dummy := await spawn_dummy(368)
	await stand(320)
	await tap(&"attack_weapon_1")
	await ticks(40)
	check(near_dummy.hit_log.size() == 1 and far_dummy.hit_log.size() == 1, "dos objetivos en la zona: cada uno recibe un golpe")

func _test_input_repeat() -> void:
	print("\n[golpe] tecla mantenida y pulsaciones repetidas")
	await load_world(true)
	inv.equip_weapon(0, sword)
	var dummy := await spawn_dummy(360)
	await stand(320)

	# Tecla mantenida: una pulsación real y las repeticiones del sistema.
	send(&"attack_weapon_1", true)
	for i in 10:
		await ticks(6)
		var echo := InputEventKey.new()
		echo.physical_keycode = KEY_Z
		echo.pressed = true
		echo.echo = true
		Input.parse_input_event(echo)
	send(&"attack_weapon_1", false)
	await ticks(30)
	check(attack_starts() == 1 and dummy.hit_log.size() == 1, "mantener la tecla un segundo produce un solo ataque")

	# Machacar la tecla durante un segundo: manda el enfriamiento de 0,4 s.
	phases.clear()
	dummy.reset_encounter()
	player.attack.cooldown_left = 0.0
	for i in 30:
		send(&"attack_weapon_1", true)
		await physics_frame
		send(&"attack_weapon_1", false)
		await physics_frame
	await ticks(40)
	var starts: int = attack_starts()
	var allowed: int = ceili(1.0 / sword.attack_cooldown)
	check(starts >= 2 and starts <= allowed, "30 pulsaciones en un segundo: %d ataques (máximo %d por enfriamiento)" % [starts, allowed])
	check(dummy.hit_log.size() == starts, "cada ataque aceptado golpea una vez (%d golpes)" % dummy.hit_log.size())
	var gaps_ok := true
	var start_frames: Array = phases.filter(func(entry): return entry[0] == P.STARTUP).map(func(entry): return entry[1])
	for i in range(1, start_frames.size()):
		gaps_ok = gaps_ok and (start_frames[i] - start_frames[i - 1]) >= floori(sword.attack_cooldown / TICK)
	check(gaps_ok, "entre ataques pasa al menos el enfriamiento del arma")

func _test_interruption_and_death() -> void:
	print("\n[jugador] interrupción, muerte y reintento")
	await load_world(true)
	inv.equip_weapon(0, sword)
	inv.equip_weapon(1, mace)
	var dummy := await spawn_dummy(360)
	await stand(320)

	# Daño recibido durante la anticipación.
	await tap(&"attack_weapon_2")
	check(player.attack.phase == P.STARTUP, "ataque en anticipación")
	var dealt: float = player.health.take_damage(5.0)
	check(dealt == 5.0 and player.attack.phase == P.IDLE and not player.attack.hitbox.active, "recibir daño interrumpe el ataque")
	check(hud.health_bar.value == 95.0, "el HUD muestra la salud tras el daño (95)")
	check(player.health.take_damage(5.0) == 0.0, "invulnerabilidad breve tras el impacto")
	await ticks(60)
	check(dummy.hit_log.is_empty() and player.current_state != player.State.ATTACK, "el ataque interrumpido no hace daño")
	check(player.health.take_damage(5.0) == 5.0, "la invulnerabilidad termina")

	# Reaparición durante la ventana activa.
	await stand(320)
	await tap(&"attack_weapon_2")
	await wait_phase(P.ACTIVE)
	check(player.attack.hitbox.active, "ventana activa abierta")
	player.respawn_at(Vector2(700, FLOOR_Y))
	check(not player.attack.hitbox.active and player.attack.phase == P.IDLE, "reaparecer cierra la zona de golpe")

	# Muerte durante la ventana activa.
	await stand(320)
	await tap(&"attack_weapon_1")
	await wait_phase(P.ACTIVE)
	player.health.invulnerable_left = 0.0
	player.health.take_damage(999.0)
	check(player.current_state == player.State.DEAD and player.sprite.animation == &"Dead", "sin salud el jugador muere")
	check(not any_hitbox_active() and player.attack.phase == P.IDLE, "morir cierra la zona de golpe")
	var starts: int = attack_starts()
	await tap(&"attack_weapon_1")
	Input.action_press(&"move_right")
	await ticks(20)
	Input.action_release(&"move_right")
	check(attack_starts() == starts and absf(player.velocity.x) < 1.0, "muerto no ataca ni se mueve")
	await ticks(ceili(world.retry_delay / TICK) + 10)
	var spawn: Vector2 = world.get_node("SpawnPoint").global_position
	check(world.retry_count == 1 and player.current_state != player.State.DEAD, "reintento automático tras la muerte")
	check(player.health.current == player.health.max_health and hud.health_bar.value == 100.0, "el reintento restaura la salud y el HUD")
	check(player.global_position.distance_to(spawn) < 1.5, "el reintento devuelve al punto de aparición")
	check(inv.weapons[0] == sword and inv.weapons[1] == mace, "el reintento conserva las armas")
	check(dummy.hit_log.is_empty() and not any_hitbox_active(), "tras el reintento no queda ninguna zona de golpe activa")

# ------------------------------------------------------------------- enemigo

func _test_enemy() -> void:
	print("\n[enemigo] patrulla, anticipación, daño, derrota y victoria")
	await load_world(false)
	var enemy: GroundEnemy = world.get_node("GroundEnemy")
	var home: Vector2 = enemy.home

	# Patrulla sin jugador cerca.
	var min_x: float = enemy.position.x
	var max_x: float = enemy.position.x
	var only_patrol := true
	for i in 600:
		await physics_frame
		min_x = minf(min_x, enemy.position.x)
		max_x = maxf(max_x, enemy.position.x)
		only_patrol = only_patrol and enemy.state == GroundEnemy.State.PATROL
	check(only_patrol and max_x - min_x > 100.0 and min_x >= home.x - enemy.patrol_distance - 2.0 and max_x <= home.x + enemy.patrol_distance + 2.0,
		"patrulla entre %.0f y %.0f sin salir de su zona" % [min_x, max_x])

	# Detección, anticipación y golpe contra un jugador desarmado y quieto.
	var enemy_phases: Array = []
	var alert_seen := false
	var player_hits: Array = []
	enemy.attack.phase_changed.connect(func(phase: int): enemy_phases.append([phase, Engine.get_physics_frames()]))
	player.health.damaged.connect(func(amount: float, _source: Node): player_hits.append([amount, Engine.get_physics_frames()]))
	enemy.patrol_distance = 400.0 # para que la persecución no dependa del empuje
	enemy.reset_encounter()
	await stand(home.x - 100.0)
	var chased := false
	for i in 600:
		await physics_frame
		chased = chased or enemy.state == GroundEnemy.State.CHASE
		if enemy.attack.phase == P.STARTUP:
			alert_seen = alert_seen or (enemy.alert.visible and enemy.blade.visible)
		if not player_hits.is_empty():
			break
	check(chased, "detecta al jugador y lo persigue")
	check(player_hits.size() == 1 and player_hits[0][0] == 15.0 and player.health.current == 85.0, "su golpe hace 15 de daño al jugador")
	var startup_frame: int = enemy_phases[0][1]
	var active_start: int = enemy_phases[1][1]
	check(enemy_phases[0][0] == P.STARTUP and active_start - startup_frame >= floori(enemy.attack_startup / TICK) - 1,
		"anticipa el golpe %.2f s antes de que haga daño" % ((active_start - startup_frame) * TICK))
	check(alert_seen, "la anticipación se ve: signo de aviso y hoja levantada")
	check(player_hits[0][1] >= active_start and player_hits[0][1] <= active_start + ceili(enemy.attack_active / TICK) + 1,
		"el daño cae dentro de su ventana activa")
	await ticks(ceili((enemy.attack_active + enemy.attack_recovery) / TICK) + 4)
	check(enemy.state != GroundEnemy.State.ATTACK and not enemy.attack.hitbox.active, "tras el golpe se recupera y cierra su zona")

	# Derrota del jugador y reintento.
	var reset_ok: Array = [false] # las lambdas capturan los locales por valor
	world.player_retried.connect(func(_p): reset_ok[0] = enemy.global_position.distance_to(home) < 1.0 \
		and enemy.health.current == enemy.health.max_health and enemy.state == GroundEnemy.State.PATROL)
	for i in 3000:
		await physics_frame
		if player.health.is_dead():
			break
	var enemy_swings: int = enemy_phases.filter(func(entry): return entry[0] == P.ACTIVE).size()
	check(player.health.is_dead() and player_hits.size() == 7, "el jugador cae tras 7 golpes de 15 (%d)" % player_hits.size())
	check(player_hits.size() <= enemy_swings, "cada golpe del enemigo daña como máximo una vez (%d golpes, %d ataques)" % [player_hits.size(), enemy_swings])
	await ticks(ceili(world.retry_delay / TICK) + 10)
	check(world.retry_count == 1 and reset_ok[0], "el reintento devuelve al enemigo a su origen con la salud completa")
	check(player.health.current == player.health.max_health and not any_hitbox_active(), "el jugador reaparece sano y sin zonas de golpe activas")

	# Victoria: tres golpes de espada.
	var enemy_hits: Array = []
	enemy.health.damaged.connect(func(amount: float, _source: Node): enemy_hits.append(amount))
	inv.equip_weapon(0, sword)
	await stand(home.x - 44.0, 1)
	for i in 900:
		await physics_frame
		if enemy.health.is_dead():
			break
		if player.attack.can_start() and absf(enemy.position.x - player.position.x) < 60.0:
			player.execute_attack(0)
	check(enemy.health.is_dead() and enemy_hits == [20.0, 20.0, 20.0], "el enemigo muere con tres golpes de espada de 20")
	check(enemy.state == GroundEnemy.State.DEAD and not enemy.visible and not enemy.attack.hitbox.active, "al morir desaparece y cierra su zona de golpe")
	check(not player.health.is_dead(), "el jugador sobrevive al duelo")
	await ticks(60)
	player.attack.cooldown_left = 0.0
	player.execute_attack(0)
	await ticks(40)
	check(enemy_hits.size() == 3 and not any_hitbox_active(), "un enemigo muerto ya no recibe golpes")
