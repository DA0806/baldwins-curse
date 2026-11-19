extends SceneTree
## Verificaciones de la etapa 1 (movimiento, cámara, recogida e inventario).
##
##   godot --headless --fixed-fps 60 --path . -s res://Tests/stage1_tests.gd
##
## Termina con código 0 si todo pasa y 1 si algo falla. Imprime las medidas
## de salto para fijar la geometría de niveles.

const WORLD_SCENE := "res://Scenes/world.tscn"
const PLAYER_SCENE := "res://Scenes/player.tscn"
const PICKUP_SCENE := "res://Scenes/Items/ItemPickup.tscn"
const SWORD := "res://Items/Weapons/Copper_Sword_test.tres"
const TICK := 1.0 / 60.0
const FLOOR_Y := 224.0 # y del jugador apoyado en el suelo (suelo en 256, medio collider 32)

var world: Node2D
var player: CharacterBody2D
var inv: PlayerInventory
var hud: InventoryHUD
var checks := 0
var failures := 0
var swap_events := 0

func _initialize() -> void:
	_run()

func _run() -> void:
	await process_frame # el árbol aún no ha arrancado dentro de _initialize
	await _test_sprites()
	await _test_jump_measures()
	await _test_coyote()
	await _test_buffer()
	await _test_ceiling()
	await _test_fall_respawn()
	await _test_pickups()
	await _test_slots()
	await _test_hud_rebind()
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

func release_all() -> void:
	for action in [&"move_left", &"move_right", &"jump"]:
		Input.action_release(action)

func load_world() -> void:
	release_all()
	if world:
		world.queue_free()
		await ticks(2)
	world = (load(WORLD_SCENE) as PackedScene).instantiate()
	root.add_child(world)
	current_scene = world
	player = world.get_node("CharacterBody2D")
	inv = player.inventory
	hud = world.get_node("InventoryHUD")
	for enemy in get_nodes_in_group(&"enemies"): # la etapa 1 se prueba sin combate
		enemy.free()
	swap_events = 0
	inv.weapon_swapped.connect(func(_s, _n, _o): swap_events += 1)
	await ticks(10)

## Coloca al jugador apoyado en el suelo en x y espera a que se asiente.
func place(x: float) -> void:
	release_all()
	player.respawn_at(Vector2(x, FLOOR_Y))
	await ticks(6)

func tap_interact() -> void:
	for pressed in [true, false]:
		var event := InputEventAction.new()
		event.action = &"interact"
		event.pressed = pressed
		Input.parse_input_event(event)
		await ticks(2)

func spawn_pickup(item: ItemData, pos: Vector2) -> ItemPickup:
	var pickup := (load(PICKUP_SCENE) as PackedScene).instantiate() as ItemPickup
	pickup.item_data = item
	pickup.position = pos
	world.add_child(pickup)
	return pickup

func make_weapon(weapon_name: String) -> WeaponData:
	var weapon := WeaponData.new()
	weapon.id = weapon_name.to_lower()
	weapon.name = weapon_name
	weapon.icon = (load(SWORD) as WeaponData).icon
	return weapon

## Objetos totales entre el suelo y el inventario.
func total_items() -> int:
	var total := 0
	for node in get_nodes_in_group(ItemPickup.GROUP):
		if node.item_data and not node.is_queued_for_deletion():
			total += 1
	for weapon in inv.weapons:
		if weapon:
			total += 1
	return total

# ------------------------------------------------------------------- sprites

func _test_sprites() -> void:
	print("\n[sprites] celdas completas y pivote en los pies")
	await load_world()
	var sprite: AnimatedSprite2D = player.get_node("AnimatedSprite2D")
	var shape: CollisionShape2D = player.get_node("CollisionShape2D")
	var collider_bottom: float = shape.position.y + (shape.shape as RectangleShape2D).size.y / 2.0
	var images := {}
	for anim in sprite.sprite_frames.get_animation_names():
		var full_cells := true
		var feet: Array[float] = []
		for i in sprite.sprite_frames.get_frame_count(anim):
			var atlas := sprite.sprite_frames.get_frame_texture(anim, i) as AtlasTexture
			full_cells = full_cells and atlas.region.size == Vector2(128, 128)
			var path: String = atlas.atlas.resource_path
			if not images.has(path):
				images[path] = Image.load_from_file(ProjectSettings.globalize_path(path))
			var used: Rect2i = (images[path] as Image).get_region(Rect2i(atlas.region)).get_used_rect()
			# Borde inferior visible en coordenadas del cuerpo (sprite centrado + offset).
			feet.append(sprite.offset.y - 64.0 + used.end.y)
		check(full_cells, "%s usa celdas de 128x128 (sin recorte)" % anim)
		if anim in [&"Jump", &"Hurt", &"Dead", &"Dash"]:
			check(feet.min() >= collider_bottom - 1 and feet.max() <= collider_bottom,
				"%s conserva su apoyo dentro de un píxel de y=%d" % [anim, collider_bottom])
		else:
			check(feet.min() >= collider_bottom - 1 and feet.max() <= collider_bottom,
				"%s mantiene los pies en y=%d en todos los cuadros" % [anim, collider_bottom])
	check(sprite.offset == Vector2(32, -32), "offset del sprite (32, -32): pivote en la celda (32, 96)")
	await place(320)
	Input.action_press(&"move_left")
	await ticks(5)
	check(sprite.flip_h and sprite.offset.x == -32.0, "al mirar a la izquierda el offset se refleja (-32)")
	release_all()

# --------------------------------------------------------------------- salto

## Salta desde el suelo. Devuelve altura máxima, ticks en el aire y x al aterrizar.
func measure_jump(hold_ticks: int) -> Dictionary:
	var start_y: float = player.position.y
	var min_y: float = start_y
	await physics_frame
	Input.action_press(&"jump")
	var air_ticks := 0
	for c in range(1, 200):
		await physics_frame
		if c == hold_ticks:
			Input.action_release(&"jump")
		min_y = minf(min_y, player.position.y)
		if c > 1 and player.is_on_floor():
			air_ticks = c
			break
	Input.action_release(&"jump")
	# La pulsación simulada se procesa un tick después y el suelo se observa uno más tarde.
	return {"height": start_y - min_y, "ticks": air_ticks, "air": air_ticks - 2, "x": player.position.x}

func _test_jump_measures() -> void:
	print("\n[salto] medidas")
	await place(320)
	var long_jump: Dictionary = await measure_jump(999)
	await place(320)
	var short_jump: Dictionary = await measure_jump(1)
	print("     altura larga %.1f px (%.2f s en el aire) · altura corta %.1f px (%.2f s)" % [
		long_jump.height, long_jump.air * TICK, short_jump.height, short_jump.air * TICK])
	check(long_jump.height > 64.0, "el salto largo supera el escalón de 64 px")
	check(short_jump.height < 32.0, "el salto corto queda por debajo del escalón de 32 px")

	var reach := {}
	for dir in [1, -1]:
		await place(100.0 if dir == 1 else 460.0)
		Input.action_press(&"move_right" if dir == 1 else &"move_left")
		await ticks(40) # alcanza la velocidad máxima
		var takeoff_x: float = player.position.x
		var jump: Dictionary = await measure_jump(999)
		reach[dir] = absf(jump.x - takeoff_x)
		release_all()
	print("     alcance horizontal a velocidad máxima: derecha %.1f px · izquierda %.1f px" % [reach[1], reach[-1]])
	check(absf(reach[1] - reach[-1]) < 1.0, "el alcance es simétrico en espejo")
	check(reach[1] > 96.0, "el alcance supera el hueco de 96 px")

func _test_coyote() -> void:
	print("\n[salto] coyote time")
	var last_ok := 0
	for k in range(4, 12): # k = ticks en el aire cuando se procesa el salto
		await place(530)
		Input.action_press(&"move_right")
		for i in 120:
			await physics_frame
			if not player.is_on_floor():
				break
		# Aquí ya pasó 1 tick en el aire y la pulsación tarda 1 tick en procesarse.
		await ticks(k - 2)
		Input.action_press(&"jump")
		await ticks(2)
		if player.velocity.y < -300.0:
			last_ok = k
	release_all()
	var expected: int = floori(player.coyote_time_max / TICK)
	print("     último salto aceptado %d ticks (%.3f s) tras dejar el borde" % [last_ok, last_ok * TICK])
	check(absi(last_ok - expected) <= 1, "coyote de %.2f s con tolerancia de un tick" % player.coyote_time_max)

func _test_buffer() -> void:
	print("\n[salto] buffer")
	await place(320)
	var flight: int = (await measure_jump(999)).ticks
	var last_ok := 0
	for j in range(5, 13): # j = ticks entre la pulsación y el salto al aterrizar
		await place(320)
		await physics_frame
		Input.action_press(&"jump")
		for c in range(1, flight + 2):
			await physics_frame
			if c == flight - j - 1: # se procesa en el tick siguiente
				Input.action_release(&"jump")
				Input.action_press(&"jump")
		if player.velocity.y < -300.0:
			last_ok = j
		release_all()
	var expected: int = floori(player.jump_buffer_max / TICK)
	print("     pulsación más temprana aceptada: %d ticks (%.3f s) antes del salto" % [last_ok, last_ok * TICK])
	check(absi(last_ok - expected) <= 1, "buffer de %.2f s con tolerancia de un tick" % player.jump_buffer_max)

func _test_ceiling() -> void:
	print("\n[salto] techo y corrección de esquinas")
	# Techo: x 800..928, cara inferior en y=160 (32 px sobre la cabeza).
	await place(864) # collider centrado bajo el techo
	var under: Dictionary = await measure_jump(999)
	check(absf(under.height - 32.0) < 1.5, "bajo el techo el salto se detiene a 32 px (%.1f)" % under.height)
	check(absf(under.x - 864.0) < 0.5, "bajo el techo no hay desplazamiento lateral")
	var shift := {}
	for side in [-1, 1]:
		# Sólo un rayo queda bajo el techo, 4 px hacia dentro del borde.
		var x: float = 792.0 if side == -1 else 936.0
		await place(x)
		var jump: Dictionary = await measure_jump(999)
		shift[side] = jump.x - x
		check(jump.height > 60.0, "borde %s: la corrección libra el techo (altura %.1f, desvío %+.1f px)" % [
			"izquierdo" if side == -1 else "derecho", jump.height, shift[side]])
	check(absf(shift[-1] + shift[1]) < 0.5 and absf(shift[1]) <= 12.0, "el desvío es simétrico y de 12 px como máximo")

# ------------------------------------------------------- caída y reaparición

func _test_fall_respawn() -> void:
	print("\n[sala] diez caídas con reaparición")
	await load_world()
	var camera: Camera2D = player.get_node("Camera2D")
	var spawn: Vector2 = world.get_node("SpawnPoint").global_position
	var good := 0
	for i in 10:
		await place(535)
		Input.action_press(&"move_right")
		while player.position.x < 575.0:
			await physics_frame
		release_all()
		var before: int = world.respawn_count
		for t in 240:
			await physics_frame
			if world.respawn_count > before:
				break
		await ticks(4)
		var at_spawn: bool = player.global_position.distance_to(spawn) < 1.5 and player.is_on_floor()
		var camera_ok: bool = camera.get_screen_center_position().distance_to(Vector2(320, 180)) < 2.0
		if world.respawn_count == before + 1 and at_spawn and camera_ok and player.velocity.length() < 1.0:
			good += 1
	check(good == 10, "10/10 caídas reaparecen en el punto con la cámara en su sitio (%d)" % good)
	check(hud.inventory_ref == inv, "el HUD sigue enlazado tras reaparecer")
	# Caminar contra cada pared con la anticipación de cámara activa.
	for dir in [1, -1]:
		await place(1740.0 if dir == 1 else 180.0)
		Input.action_press(&"move_right" if dir == 1 else &"move_left")
		var worst: float = 0.0
		for t in 180:
			await physics_frame
			var center: Vector2 = camera.get_screen_center_position()
			worst = maxf(worst, maxf(320.0 - center.x, center.x - 1600.0))
			worst = maxf(worst, absf(center.y - 180.0))
		release_all()
		check(worst < 0.5, "la vista no sale de la sala al caminar contra la pared %s (exceso %.1f px)" % [
			"derecha" if dir == 1 else "izquierda", worst])

# ------------------------------------------------------------------ recogida

func _test_pickups() -> void:
	print("\n[recogida] un objetivo por pulsación")
	await load_world()
	var sword: WeaponData = load(SWORD)
	var pickup_1: ItemPickup = world.get_node("ItemPickup")
	var pickup_2: ItemPickup = world.get_node("ItemPickup2")
	var label_1: Label = pickup_1.get_node("Label")
	check(not label_1.visible, "el aviso está oculto fuera de rango")
	check(total_items() == 2, "dos objetos al empezar")

	await place(186)
	check(label_1.visible and label_1.text == "[R] Copper Sword", "aviso en rango con la tecla del InputMap: '%s'" % label_1.text)
	await tap_interact()
	check(inv.weapons[0] == sword and inv.weapons[1] == null, "hueco libre: la primera espada entra en la ranura 0")
	check(not is_instance_valid(pickup_1), "el pickup recogido desaparece")
	check(hud.weapon_icon_0.visible and not hud.weapon_icon_1.visible, "el HUD muestra la ranura 0")

	var second: WeaponData = pickup_2.item_data
	await place(468)
	await tap_interact()
	check(inv.weapons[1] == second and not is_instance_valid(pickup_2), "la segunda arma entra en la ranura 1")
	check(swap_events == 2 and total_items() == 2, "dos transacciones, total de objetos conservado")

	# Intercambio con inventario lleno.
	var blade := make_weapon("Blade")
	var floor_pos := Vector2(player.position.x, 230)
	var pickup_a := spawn_pickup(blade, floor_pos)
	await ticks(4)
	await tap_interact()
	var label_a: Label = pickup_a.get_node("Label")
	check(inv.weapons[0] == blade and inv.weapons[1] == second, "inventario lleno: intercambia en la ranura de intercambio (0)")
	check(is_instance_valid(pickup_a) and pickup_a.item_data == sword, "el arma desplazada queda en el suelo")
	check(label_a.visible and label_a.text == "[R] Copper Sword", "el aviso del objeto desplazado sigue visible")
	check(pickup_a.get_node("Sprite2D").texture == sword.world_texture, "el pickup muestra la textura de mundo del objeto desplazado")
	check(total_items() == 3, "el intercambio conserva el total de objetos")

	# Dos pickups solapados: una pulsación, una transacción.
	var axe := make_weapon("Axe")
	var pickup_b := spawn_pickup(axe, floor_pos)
	await ticks(4)
	swap_events = 0
	await tap_interact()
	check(swap_events == 1, "pickups solapados: una pulsación produce una sola transacción")
	check(pickup_a.item_data == blade and pickup_b.item_data == axe, "empate de distancia: gana el primero en orden de árbol")
	pickup_a.position.x += 12.0
	await ticks(4)
	swap_events = 0
	await tap_interact()
	check(swap_events == 1 and pickup_b.item_data == sword and pickup_a.item_data == blade, "se elige el pickup más cercano")
	check(total_items() == 4, "total conservado tras los intercambios")

	# Ranura de intercambio distinta.
	inv.active_weapon_slot = 1
	swap_events = 0
	await tap_interact()
	check(swap_events == 1 and inv.weapons[1] == sword and inv.weapons[0] == axe, "con ranura de intercambio 1 se reemplaza la ranura 1")
	inv.active_weapon_slot = 0

	# Objeto nulo y tipo sin manejador.
	var before: Array = inv.weapons.duplicate()
	var odd_pickup := spawn_pickup(null, Vector2(1200, 230))
	await place(1200)
	swap_events = 0
	await tap_interact()
	check(swap_events == 0 and is_instance_valid(odd_pickup), "pickup sin objeto: nada cambia")
	var odd := ItemData.new()
	odd.name = "Raro"
	odd_pickup.item_data = odd
	await tap_interact()
	check(swap_events == 0 and is_instance_valid(odd_pickup) and odd_pickup.item_data == odd and inv.weapons == before,
		"tipo sin manejador: el pickup y el inventario quedan sin cambios")

func _test_slots() -> void:
	print("\n[inventario] invariante de dos ranuras")
	var bag := PlayerInventory.new()
	root.add_child(bag)
	var sword: WeaponData = load(SWORD)
	var blade := make_weapon("Blade")
	var empty: Array[WeaponData] = []
	bag.weapons = empty
	check(bag.weapons.size() == 2, "un arreglo vacío se normaliza a dos ranuras")
	var many: Array[WeaponData] = [sword, blade, sword]
	bag.weapons = many
	check(bag.weapons.size() == 2 and bag.weapons[1] == blade, "un arreglo de tres se recorta a dos")
	bag.active_weapon_slot = 7
	check(bag.active_weapon_slot == 1, "ranura de intercambio 7 se ajusta a 1")
	bag.active_weapon_slot = -3
	check(bag.active_weapon_slot == 0, "ranura de intercambio -3 se ajusta a 0")
	bag.weapons.clear() # modificación en sitio, sin pasar por el setter
	check(bag.get_weapon(0) == null and bag.get_weapon(5) == null, "leer una ranura inválida devuelve vacío sin error")
	check(bag.equip_weapon(5, sword) == null and bag.weapons == [null, null], "equipar en una ranura inválida se rechaza")
	# Hueco 0 vacío con ranura de intercambio 1 ocupada (caso de la auditoría).
	bag.equip_weapon(1, sword)
	bag.active_weapon_slot = 1
	var dropped: WeaponData = bag.equip_or_swap_weapon(blade)
	check(dropped == null and bag.weapons[0] == blade and bag.weapons[1] == sword, "se llena primero el hueco libre aunque la ranura de intercambio sea otra")
	check(bag.pick_up_item(null).status == PlayerInventory.PickupStatus.REJECTED and bag.equip_or_swap_weapon(null) == null,
		"un objeto nulo se rechaza sin tocar el inventario")
	var jump_events: Array = ProjectSettings.get_setting("input/jump")["events"]
	check(not jump_events.has(null) and jump_events.size() == 2, "la acción jump ya no trae un evento nulo")
	bag.queue_free()

# ----------------------------------------------------------------------- HUD

func _test_hud_rebind() -> void:
	print("\n[HUD] enlace idempotente")
	await load_world()
	var weapon_connections := inv.weapon_swapped.get_connections().size()
	var swap_connections := inv.swap_slot_changed.get_connections().size()
	for i in 3:
		hud.setup_inventory(inv)
	check(inv.weapon_swapped.get_connections().size() == weapon_connections and inv.swap_slot_changed.get_connections().size() == swap_connections,
		"reenlazar el mismo inventario no duplica conexiones")
	check(hud.weapon_key_labels[0].text == "[Z]" and hud.weapon_key_labels[1].text == "X" and hud.mask_key_label.text == "C/V",
		"las teclas del HUD salen del InputMap y marcan la ranura de intercambio")
	inv.active_weapon_slot = 1
	check(hud.weapon_key_labels[0].text == "Z" and hud.weapon_key_labels[1].text == "[X]", "el HUD sigue a la ranura de intercambio")
	inv.equip_weapon(0, load(SWORD))
	check(hud.weapon_icon_0.visible, "el HUD refleja el arma equipada")

	# Reemplazo del jugador: el nuevo se enlaza solo y el anterior se desconecta.
	var old_inv := inv
	var position: Vector2 = player.position
	world.remove_child(player)
	var new_player := (load(PLAYER_SCENE) as PackedScene).instantiate() as CharacterBody2D
	new_player.position = position
	world.add_child(new_player)
	await ticks(2)
	var new_inv: PlayerInventory = new_player.inventory
	check(hud.inventory_ref == new_inv, "el HUD se enlaza al inventario del jugador nuevo")
	check(old_inv.swap_slot_changed.get_connections().is_empty(), "el inventario anterior queda desconectado")
	check(not hud.weapon_icon_0.visible and hud.weapon_key_labels[0].text == "[Z]", "el HUD muestra el estado del inventario nuevo")
	new_inv.equip_weapon(1, load(SWORD))
	check(hud.weapon_icon_1.visible, "las señales del inventario nuevo actualizan el HUD")
	player.free()
