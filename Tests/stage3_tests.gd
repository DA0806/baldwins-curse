extends SceneTree
## Verificaciones de la etapa 3 (máscaras, punto de control, circuito y final).
##
##   godot --headless --fixed-fps 60 --path . -s res://Tests/stage3_tests.gd
##
## Termina con código 0 si todo pasa y 1 si algo falla.

const WORLD_SCENE := "res://Scenes/world.tscn"
const SWORD := "res://Items/Weapons/Copper_Sword_test.tres"
const VOW := "res://Items/Masks/Mask_Vow.tres"
const EMBER := "res://Items/Masks/Mask_Ember.tres"
const P := MeleeAttack.Phase

var session: RunSession
var player: CharacterBody2D
var inv: PlayerInventory
var sword: WeaponData
var vow: MaskData
var ember: MaskData
var checks := 0
var failures := 0

func _initialize() -> void:
	_run()

func _run() -> void:
	await process_frame
	SaveGame.directory = "user://tests/"
	# Con `-s` el autoload puede no existir: se crea igual que lo haría Godot.
	session = root.get_node_or_null("GameSession") as RunSession
	if not session:
		session = (load("res://Scripts/GameSession.gd") as GDScript).new()
		session.name = "GameSession"
		root.add_child(session)
	sword = load(SWORD)
	vow = load(VOW)
	ember = load(EMBER)
	await _test_resources()
	await _test_damage_modifiers()
	await _test_switch_during_attack()
	await _test_cycle_and_cooldown()
	await _test_capacity_and_state()
	await _test_circuit()
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

func tap(action: StringName) -> void:
	var event := InputEventAction.new()
	event.action = action
	event.pressed = true
	Input.parse_input_event(event)
	await ticks(2)
	event = event.duplicate()
	event.pressed = false
	Input.parse_input_event(event)
	await ticks(1)

## Espera a que la escena actual sea `expected` y distinta de la anterior.
func wait_scene(expected: String, previous_id: int = 0) -> Node:
	for i in 300:
		await process_frame
		var scene := current_scene
		if scene and scene.get_instance_id() != previous_id and scene.name == expected and scene.is_node_ready():
			await ticks(3)
			_bind_player(scene)
			return scene
	return null

func _bind_player(scene: Node) -> void:
	var found = scene.get_node_or_null("CharacterBody2D")
	if found:
		player = found
		inv = player.inventory

func set_masks(masks: Array[MaskData], index: int = 0) -> void:
	inv.carried_masks = masks
	inv.active_mask_index = index
	inv.mask_swap_timer = 0.0
	inv.mask_changed.emit(inv.get_active_mask(), null)

## Coloca al jugador y deja correr la física para que las áreas lo detecten.
func place(at: Vector2, settle: int = 4) -> void:
	player.respawn_at(at)
	await ticks(settle)

func wait_idle() -> void:
	for i in 180:
		if player.attack.phase == P.IDLE and player.attack.cooldown_left <= 0.0:
			return
		await physics_frame

func wait_phase(phase: int) -> void:
	for i in 120:
		if player.attack.phase == phase:
			return
		await physics_frame

# ---------------------------------------------------------------- pruebas

func _test_resources() -> void:
	print("\n# Recursos de máscara")
	check(vow.id == "mask_vow" and ember.id == "mask_ember", "IDs estables mask_vow y mask_ember")
	check(vow.icon != null and ember.icon != null and vow.icon != ember.icon, "iconos distintos")
	check(ItemCatalog.get_item("mask_vow") == vow and ItemCatalog.get_item("copper_sword") == sword, "ItemCatalog resuelve los IDs")
	check(ItemCatalog.get_item("") == null, "ID vacío = nada")

func _load_lab() -> void:
	change_scene_to_file(WORLD_SCENE)
	var lab := await wait_scene("World")
	var enemy := lab.get_node_or_null("GroundEnemy")
	if enemy:
		enemy.free()
	inv.weapons = [sword, null]
	set_masks([])
	await place(Vector2(320, 224), 20)

func _test_damage_modifiers() -> void:
	print("\n# Modificadores (daño base 20)")
	await _load_lab()
	var health: Health = player.health
	health.reset()
	check(is_equal_approx(health.take_damage(20.0), 20.0), "sin máscara recibe 20")
	set_masks([vow])
	health.reset()
	check(is_equal_approx(health.take_damage(20.0), 16.0), "Voto: recibe 16")
	set_masks([ember])
	health.reset()
	check(is_equal_approx(health.take_damage(20.0), 20.0), "Ascua no cambia el daño recibido")
	health.reset()
	await place(Vector2(320, 224), 30)
	check(player.execute_attack(0) and is_equal_approx(player.attack.spec.damage, 25.0), "Ascua: el ataque de 20 se fija en 25")
	await wait_idle()
	set_masks([vow])
	check(player.execute_attack(0) and is_equal_approx(player.attack.spec.damage, 20.0), "Voto no cambia el daño de arma")
	await wait_idle()

func _test_switch_during_attack() -> void:
	print("\n# Cambio de máscara durante un ataque")
	var dummy: TrainingDummy = current_scene.get_node("TrainingDummy")
	await place(Vector2(320, 224), 10)
	dummy.position = Vector2(350, 232)
	dummy.reset_encounter()
	await ticks(2)
	set_masks([ember, vow])
	check(player.execute_attack(0), "ataque con Ascua aceptado")
	await ticks(2)
	inv.cycle_mask(1)
	check(inv.get_active_mask() == vow and player.attack.phase == P.STARTUP, "cambia a Voto durante la anticipación")
	await wait_phase(P.RECOVERY)
	check(dummy.hit_log.size() == 1 and is_equal_approx(dummy.hit_log.back().damage, 25.0), "el golpe conserva 25 (Ascua al iniciar)")
	await wait_idle()
	inv.mask_swap_timer = 0.0
	check(player.execute_attack(0), "ataque con Voto aceptado")
	await ticks(2)
	inv.cycle_mask(-1)
	check(inv.get_active_mask() == ember, "cambia a Ascua durante la anticipación")
	await wait_phase(P.RECOVERY)
	check(dummy.hit_log.size() == 2 and is_equal_approx(dummy.hit_log.back().damage, 20.0), "el golpe conserva 20 (Voto al iniciar)")
	await wait_idle()

func _test_cycle_and_cooldown() -> void:
	print("\n# Ciclo y enfriamiento")
	var changes := [0]
	var count := func(_a, _b): changes[0] += 1
	inv.mask_changed.connect(count)
	set_masks([])
	changes[0] = 0
	check(inv.cycle_mask(1) == null and inv.mask_swap_timer == 0.0 and changes[0] == 0, "lista vacía: nada cambia ni se consume")
	set_masks([vow])
	changes[0] = 0
	check(inv.cycle_mask(1) == vow and inv.mask_swap_timer == 0.0 and changes[0] == 0, "una máscara: nada cambia ni se consume")

	set_masks([vow, ember])
	changes[0] = 0
	await tap(&"next_mask")
	check(inv.get_active_mask() == ember and changes[0] == 1, "tecla siguiente cambia a Ascua")
	check(inv.mask_swap_timer > 0.9 and inv.get_mask_cooldown_ratio() > 0.9, "empieza 1 s de enfriamiento")
	await tap(&"prev_mask")
	check(inv.get_active_mask() == ember and changes[0] == 1, "durante el enfriamiento se ignora")
	await process_frame
	var hud: InventoryHUD = current_scene.get_node("InventoryHUD")
	check(hud.mask_cooldown_bar.visible and hud.mask_name_label.text == "Máscara de Ascua", "el HUD muestra recarga y nombre")
	check(hud.mask_effect_label.text == ember.description and hud.mask_icon.texture == ember.icon, "el HUD muestra efecto e icono")
	await ticks(50)
	check(inv.cycle_mask(-1) == ember, "a los ~0,9 s sigue bloqueado")
	await ticks(12)
	check(inv.mask_swap_timer == 0.0 and inv.cycle_mask(-1) == vow, "pasado 1 s vuelve a cambiar")
	await process_frame
	check(hud.mask_name_label.text == "Máscara del Voto", "el HUD sigue el cambio")

	var test_mask := MaskData.new()
	test_mask.id = "test_mask"
	test_mask.swap_cooldown = 1.0
	set_masks([vow, ember, test_mask])
	var order: Array = []
	for step in 3:
		inv.mask_swap_timer = 0.0
		order.append(inv.cycle_mask(1).id)
	check(order == ["mask_ember", "test_mask", "mask_vow"], "siguiente da la vuelta: %s" % [order])
	inv.mask_swap_timer = 0.0
	check(inv.cycle_mask(-1) == test_mask, "anterior da la vuelta desde la primera")
	inv.mask_changed.disconnect(count)
	set_masks([])

func _test_capacity_and_state() -> void:
	print("\n# Capacidad y estado por IDs")
	var test_mask := MaskData.new()
	test_mask.id = "test_mask"
	var extra := MaskData.new()
	extra.id = "test_extra"
	set_masks([vow, ember, test_mask], 1)
	var dropped := inv.add_or_swap_mask(extra)
	check(dropped == ember and inv.carried_masks[1] == extra and inv.carried_masks.size() == 3, "lleno: reemplaza la activa y devuelve la desplazada")
	var old_max := inv.max_carried_masks
	inv.max_carried_masks = 0
	check(inv.max_carried_masks == 1, "la capacidad nunca baja de 1")
	inv.max_carried_masks = old_max

	set_masks([vow, ember], 1)
	inv.weapons = [null, sword]
	inv.active_weapon_slot = 1
	var state := inv.to_state()
	check(state == {"weapons": ["", "copper_sword"], "swap_slot": 1, "masks": ["mask_vow", "mask_ember"], "active_mask": 1}, "to_state sólo guarda IDs")
	inv.weapons = [null, null]
	set_masks([])
	inv.from_state(state)
	check(inv.get_weapon(1) == sword and inv.get_weapon(0) == null and inv.active_weapon_slot == 1, "from_state restaura armas y ranura")
	check(inv.carried_masks == [vow, ember] and inv.get_active_mask() == ember, "from_state restaura máscaras y la activa")
	inv.from_state({"weapons": ["nope", ""], "masks": ["nope"]})
	check(inv.get_weapon(0) == null and inv.carried_masks.is_empty(), "IDs desconocidos se omiten sin romper")

func _test_circuit() -> void:
	print("\n# Circuito: partida normal y reintentos")
	session.new_run()
	var room := await wait_scene("Atrio1")
	check(room != null and session.run_active and session.checkpoint.get("spawn_id") == "start", "partida nueva en Atrio1 con punto inicial")
	check(inv.get_weapon(0) == null and inv.carried_masks.is_empty(), "empieza sin equipo")

	await place(Vector2(220, 224))
	check(player.try_interact() == PlayerInventory.PickupStatus.STORED and inv.get_weapon(0) == sword, "recoge la espada")
	await place(Vector2(780, 224))
	var dummy: TrainingDummy = room.get_node("TrainingDummy")
	dummy.position = Vector2(810, 232)
	await ticks(2)
	check(player.execute_attack(0), "ataca al maniquí")
	await wait_phase(P.RECOVERY)
	check(dummy.hit_log.size() == 1, "el maniquí registra el golpe")
	await wait_idle()

	var previous := room.get_instance_id()
	await place(Vector2(1256, 224), 1)
	room = await wait_scene("Atrio2", previous)
	check(room != null and inv.get_weapon(0) == sword and inv.carried_masks.is_empty(), "la salida lleva el equipo a Atrio2")
	check(player.global_position.distance_to(Vector2(48, 224)) < 4.0, "aparece en from_atrio_1")

	await place(Vector2(150, 224))
	check(session.is_active_checkpoint("atrio_2", "checkpoint_atrio_2"), "activa el punto de control")
	check(session.checkpoint.collected.has("atrio_1/copper_sword") and session.checkpoint.inventory.weapons == ["copper_sword", ""], "guarda recogidas y armas")

	await place(Vector2(700, 224))
	check(player.try_interact() == PlayerInventory.PickupStatus.STORED and inv.carried_masks == [vow], "recoge el Voto (después del punto)")
	player.health.take_damage(1000.0)
	previous = room.get_instance_id()
	room = await wait_scene("Atrio2", previous)
	check(room != null and session.retries == 1, "morir restaura el punto de control")
	check(player.global_position.distance_to(Vector2(150, 224)) < 4.0, "reaparece en la llama")
	check(inv.carried_masks.is_empty() and inv.get_weapon(0) == sword, "inventario del punto (sin el Voto posterior)")
	check(is_equal_approx(player.health.current, player.health.max_health), "salud completa de reaparición")
	check(room.get_node_or_null("MaskVow") != null, "el Voto no guardado vuelve a estar en el suelo")

	await place(Vector2(700, 224))
	player.try_interact()
	await place(Vector2(300, 224))
	await place(Vector2(150, 224))
	check(session.checkpoint.inventory.masks == ["mask_vow"], "reactivar el punto guarda el Voto")
	await place(Vector2(448, 290), 1)
	previous = room.get_instance_id()
	room = await wait_scene("Atrio2", previous)
	check(room != null and session.retries == 2, "caer restaura el punto de control")
	check(inv.carried_masks == [vow], "sin máscaras duplicadas tras el reintento")
	await process_frame
	check(room.get_node_or_null("MaskVow") == null, "el Voto guardado no reaparece")
	await place(Vector2(700, 224))
	check(player.try_interact() == PlayerInventory.PickupStatus.REJECTED, "no se puede recoger dos veces")

	previous = room.get_instance_id()
	await place(Vector2(1256, 224), 1)
	room = await wait_scene("Atrio3", previous)
	check(room != null, "llega a Atrio3")
	var encounter := room.get_node("Encounter")
	var guard := encounter.get_node("Guard")
	check(guard.health.max_health == 100.0 and guard.attack_damage == 20.0, "guardián: 100 de salud y golpe de 20")
	set_masks([vow, ember], 0)
	check(is_equal_approx(player.hurtbox.receive_hit(guard.attack_damage, guard), 16.0), "su golpe con Voto quita 16")
	player.health.reset()
	await place(Vector2(1256, 224), 1)
	check(room.get_node_or_null("Gate") != null, "la reja cierra la salida")
	for enemy in [guard, encounter.get_node("Raider")]:
		enemy.health.take_damage(1000.0)
	await ticks(2)
	check(encounter.is_cleared() and room.get_node_or_null("Gate") == null, "vencer a ambos abre la reja")
	previous = room.get_instance_id()
	await place(Vector2(928, 224), 1)
	room = await wait_scene("Cripta1", previous)
	check(room != null and inv.carried_masks == [vow, ember], "la reja abierta lleva a la Cripta con el equipo")

	# El final (epílogo en la etapa 5) y la vuelta al inicio.
	previous = room.get_instance_id()
	session.finish_run()
	var ending := await wait_scene("Ending", previous)
	check(ending != null and session.finished, "terminar la partida lleva al final")
	check(ending != null and ending.get_node("Stats").text.contains("Reintentos 2"), "el final muestra los reintentos")
	await tap(&"interact")
	var title := await wait_scene("TitleScreen")
	check(title != null, "el final vuelve al título")
	session.start_campaign()
	var intro := await wait_scene("Intro")
	await tap(&"interact")
	room = await wait_scene("Atrio1")
	check(room != null and inv.get_weapon(0) == null and session.collected.is_empty(), "volver a empezar limpia el estado")
	check(room != null and room.get_node_or_null("Sword") != null, "los objetos vuelven en la partida nueva")
