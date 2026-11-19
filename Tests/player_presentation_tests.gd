extends SceneTree
## Tests phase-driven equipment with synthetic poses; default also tests the real player.

const VIEW_PATH := "res://Scripts/Presentation/BaldwinPresentation.gd"
const COUNTS := {
	"Idle": 8, "Walk": 16, "Jump": 10, "Hurt": 6, "Dead": 12, "Dash": 12,
	"AttackSwordStartup": 6, "AttackSwordActive": 4, "AttackSwordRecovery": 6,
	"AttackMaceStartup": 8, "AttackMaceActive": 4, "AttackMaceRecovery": 8,
}
var checks := 0
var failures := 0

# Start after autoloads are ready and keep persistence in the test directory.
func _initialize() -> void:
	_run()

# Exercise the real player when generated resources exist, plus isolated presentation contracts.
func _run() -> void:
	await process_frame
	SaveGame.directory = "user://tests/"
	if not "--fixture-only" in OS.get_cmdline_user_args():
		await _test_player()
	if ResourceLoader.exists(VIEW_PATH):
		_test_layers()
		await _test_pickup()
	else:
		check(false, "separate body/equipment presentation exists")
	print("\n== %d presentation checks, %d failures ==" % [checks, failures])
	quit(1 if failures else 0)

# Report every assertion without abandoning the remaining checks.
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures += 1
	print("  %s %s" % ["ok" if ok else "FAIL", message])

# Advance actual combat clocks rather than simulating phase callbacks.
func ticks(count: int) -> void:
	for i in count:
		await physics_frame

# Catch the old behavior where every weapon shared the sword's last attack frame.
func _test_player() -> void:
	var world := (load("res://Scenes/world.tscn") as PackedScene).instantiate()
	root.add_child(world)
	current_scene = world
	for enemy in get_nodes_in_group(&"enemies"):
		enemy.free()
	var player = world.get_node("CharacterBody2D")
	player.inventory.equip_weapon(0, load("res://Items/Weapons/Copper_Sword_test.tres"))
	player.inventory.equip_weapon(1, load("res://Items/Weapons/Crypt_Mace.tres"))
	await ticks(3)
	player.execute_attack(1)
	check(player.sprite.animation == &"AttackMaceStartup", "maza accepts its own windup clip")
	var seen := {}
	for i in 60:
		await physics_frame
		if player.attack.phase != MeleeAttack.Phase.IDLE:
			seen[player.attack.phase] = player.sprite.animation
	check(seen.get(MeleeAttack.Phase.ACTIVE) == &"AttackMaceActive", "mace active art matches its real damage window")
	check(seen.get(MeleeAttack.Phase.RECOVERY) == &"AttackMaceRecovery", "mace has a moving recovery instead of holding the strike")
	player.velocity.x = 45.0
	player._update_locomotion_visual()
	player.sprite.frame = 3
	player.velocity.x = 60.0
	player._update_locomotion_visual()
	var walk_entry: Dictionary = player.presentation.pose_data.get("Walk", {})
	var walk_cycle_distance: float = 60.0 * player.sprite.sprite_frames.get_frame_count(&"Walk") / (player.sprite.sprite_frames.get_animation_speed(&"Walk") * player.sprite.speed_scale)
	var cadence_ok: bool = is_equal_approx(walk_cycle_distance, float(walk_entry.stride_px)) if walk_entry.has("stride_px") else is_equal_approx(player.sprite.speed_scale, 2.0 / 3.0)
	check(player.sprite.animation == &"Walk" and player.sprite.frame == 3 and cadence_ok,
		"acceleration changes walk cadence without restarting its body clock")
	if player.sprite.sprite_frames.has_animation(&"Run"):
		player.velocity.x = 180.0
		player._update_locomotion_visual()
		var run_entry: Dictionary = player.presentation.pose_data["Run"]
		var run_cycle_distance: float = 180.0 * player.sprite.sprite_frames.get_frame_count(&"Run") / (player.sprite.sprite_frames.get_animation_speed(&"Run") * player.sprite.speed_scale)
		var run_cadence_ok: bool = is_equal_approx(run_cycle_distance, float(run_entry.stride_px)) if run_entry.has("stride_px") else is_equal_approx(player.sprite.speed_scale, 1.0)
		check(player.sprite.animation == &"Run" and run_cadence_ok, "fast locomotion selects a run whose stride matches world movement")
		player.sprite.frame = 4
		player.velocity.x = 150.0
		player._update_locomotion_visual()
		check(player.sprite.animation == &"Run" and player.sprite.frame == 4, "changing run speed preserves frame continuity")
	world.free()
	current_scene = null

# Build known positions independently of generated artwork for deterministic layer checks.
func fixture_data() -> Dictionary:
	var data := {}
	for clip in COUNTS:
		var poses := []
		for index in COUNTS[clip]:
			poses.append({"hand": [10 + index, -10], "angle": 0.2 * index,
				"weapon_visible": clip != "Dead" or index < 5})
		data[clip] = {"count": COUNTS[clip], "fps": 10.0, "loop": clip in ["Idle", "Walk"], "poses": poses}
	return data

# Use a distinguishable real texture for each equipment layer.
func fixture_texture(color: Color, size := Vector2i(64, 32)) -> Texture2D:
	var image := Image.create(size.x, size.y, false, Image.FORMAT_RGBA8)
	image.fill(color)
	return ImageTexture.create_from_image(image)

# Verify equipment snapshots, one visual clock, mirroring and death visibility.
func _test_layers() -> void:
	var host := Node2D.new()
	root.add_child(host)
	var body := AnimatedSprite2D.new()
	body.offset = Vector2(32, -32)
	body.sprite_frames = SpriteFrames.new()
	body.sprite_frames.remove_animation(&"default")
	var data := fixture_data()
	for clip in data:
		body.sprite_frames.add_animation(clip)
		body.sprite_frames.set_animation_speed(clip, 10)
		for i in COUNTS[clip]:
			body.sprite_frames.add_frame(clip, fixture_texture(Color.WHITE, Vector2i(128, 128)))
	host.add_child(body)
	var bag := PlayerInventory.new()
	host.add_child(bag)
	var sword := WeaponData.new()
	sword.combo_animation_tag = "slash"
	sword.set("equipped_texture", fixture_texture(Color.RED))
	var mace := WeaponData.new()
	mace.combo_animation_tag = "mace"
	mace.set("equipped_texture", fixture_texture(Color.BLUE))
	bag.equip_weapon(0, sword)
	bag.equip_weapon(1, mace)
	var view = (load(VIEW_PATH) as GDScript).new()
	host.add_child(view)
	view.setup(body, bag, data)
	view.play_actor(&"Idle")
	check(view.displayed_weapon == sword and view.weapon_sprite.texture == sword.get("equipped_texture"), "first occupied slot supplies resting equipment")
	var spec := MeleeAttack.Spec.new()
	spec.startup = 0.16
	spec.active = 0.08
	spec.recovery = 0.16
	view.begin_attack(sword, 1)
	view.play_attack_phase(MeleeAttack.Phase.STARTUP, spec)
	check(body.animation == &"AttackSwordStartup" and is_equal_approx(body.speed_scale, 3.75), "sword windup fills exactly the accepted startup duration")
	body.frame = 3
	check(view.weapon_sprite.position == Vector2(13, -10) and is_equal_approx(view.weapon_sprite.rotation, 0.6), "equipment moves from the body's actual frame_changed signal")
	bag.equip_weapon(0, null)
	check(view.weapon_sprite.texture == sword.get("equipped_texture"), "removing an accepted weapon cannot change an in-flight attack")
	view.play_attack_phase(MeleeAttack.Phase.ACTIVE, spec)
	check(body.animation == &"AttackSwordActive" and body.frame == 0, "active phase starts its own body frames")
	view.play_attack_phase(MeleeAttack.Phase.RECOVERY, spec)
	check(body.animation == &"AttackSwordRecovery", "recovery uses its own clip")
	view.end_attack()
	view.play_actor(&"Idle")
	check(view.displayed_weapon == mace, "removed resting weapon falls back to the remaining slot")
	view.begin_attack(mace, -1)
	view.play_attack_phase(MeleeAttack.Phase.STARTUP, spec)
	body.frame = 3
	check(body.animation == &"AttackMaceStartup" and body.flip_h and body.offset.x == -32,
		"mace gesture and body orientation are captured together")
	check(view.weapon_sprite.position == Vector2(-13, -10) and view.weapon_sprite.scale.x == -1
		and is_equal_approx(view.weapon_sprite.rotation, -0.6), "left-facing weapon mirrors around its grip without a position jump")
	view.end_attack()
	view.play_actor(&"Hurt")
	check(body.animation == &"Hurt" and is_equal_approx(body.speed_scale, 1.0), "cancel restores the normal visual clock for damage")
	view.play_actor(&"Dead")
	body.frame = 11
	check(not view.weapon_sprite.visible, "final death pose does not leave equipment floating in the hand")
	view.play_actor(&"Idle")
	check(view.weapon_sprite.visible, "revive restores the carried equipment")
	bag.equip_weapon(1, null)
	check(not view.weapon_sprite.visible, "empty inventory hides resting equipment")
	host.free()

# Keep world art independent from HUD art while supporting external item resources.
func _test_pickup() -> void:
	var pickup := (load("res://Scenes/Items/ItemPickup.tscn") as PackedScene).instantiate()
	var item := ItemData.new()
	item.icon = fixture_texture(Color.WHITE, Vector2i(64, 64))
	item.set("world_texture", fixture_texture(Color.RED, Vector2i(24, 24)))
	pickup.item_data = item
	root.add_child(pickup)
	await process_frame
	check(pickup.sprite.texture == item.get("world_texture") and pickup.sprite.scale == Vector2.ONE,
		"pickup uses pixel-sized world art, leaving HUD icon and interaction area unchanged")
	item.set("world_texture", null)
	pickup.update_appearance()
	check(pickup.sprite.texture == item.icon, "external resources without world art keep their icon fallback")
	pickup.free()
