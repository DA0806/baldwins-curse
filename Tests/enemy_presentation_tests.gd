extends SceneTree
## Tests presentation against the real combat/state clocks, using tiny local pose fixtures.

const HELPER := "res://Scripts/Presentation/EnemyPresentation.gd"
var checks := 0
var failures := 0

# Start after autoloads have entered the tree.
func _initialize() -> void:
	_run()

# Exercise frame selection, mirrored equipment, state transitions and floor anchors.
func _run() -> void:
	await process_frame
	check(ResourceLoader.exists(HELPER), "enemy presentation supports layered animation")
	if not ResourceLoader.exists(HELPER):
		quit(1)
		return
	_test_clock_and_equipment()
	_test_grid_atlas()
	await _test_ground_phases()
	await _test_ranged_and_boss_states()
	print("\n== %d comprobaciones, %d fallas ==" % [checks, failures])
	quit(1 if failures else 0)

# Record failures without stopping at the first assertion.
func check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures += 1
	print("  %s %s" % ["ok  " if condition else "FAIL", label])

# Make a real body atlas; pose coordinates vary so stale equipment frames are detectable.
func _fixture(cell: Vector2i, root_point: Vector2i, clips: Dictionary, count: int, weapon_name: String) -> Dictionary:
	var poses := []
	for frame in count:
		poses.append({"hand": [frame, -8], "angle": 0.25, "weapon": weapon_name,
			"weapon_visible": true, "weapon_scale": 0.65})
	return {"cell": [cell.x, cell.y], "root": [root_point.x, root_point.y],
		"clips": clips, "poses": poses}

# Attach the renderer fixture before the actor enters the tree.
func _body(actor: Node2D, definition: Dictionary) -> Sprite2D:
	var cell: Array = definition.cell
	var columns: int = int(definition.get("columns", definition.poses.size()))
	var rows: int = int(definition.get("rows", 1))
	var image := Image.create(int(cell[0]) * columns, int(cell[1]) * rows, false, Image.FORMAT_RGBA8)
	image.fill(Color.WHITE)
	var art := Sprite2D.new()
	art.name = "Art"
	art.texture = ImageTexture.create_from_image(image)
	actor.add_child(art)
	return art

# Catch resetting the loop on every update or reading a different frame for equipment.
func _test_clock_and_equipment() -> void:
	var actor := Node2D.new()
	root.add_child(actor)
	var definition := _fixture(Vector2i(16, 16), Vector2i(8, 12), {
		"Idle": {"start": 0, "count": 2, "fps": 2.0, "loop": true},
		"Startup": {"start": 2, "count": 3, "fps": 10.0, "loop": false},
		"Active": {"start": 5, "count": 2, "fps": 10.0, "loop": false},
		"Dead": {"start": 7, "count": 1, "fps": 10.0, "loop": false},
	}, 8, "sword")
	definition.poses[7].weapon_visible = false
	var art := _body(actor, definition)
	var presenter = load(HELPER).new(art, definition)
	presenter.update("Idle", 0.0, 1)
	presenter.update("Idle", 0.75, 1)
	check(art.frame == 1, "idle advances without restarting on repeated updates")
	presenter.update("Startup", 0.0, 1, 0.6, 0.5)
	check(art.frame == 3, "startup samples its own range from authoritative phase progress")
	var weapon: Sprite2D = actor.get_node("WeaponArt")
	check(weapon.position == Vector2(3, -8), "body and weapon consume the same sampled pose")
	presenter.update("Startup", 0.0, -1, 0.6, 0.5)
	check(art.frame == 3 and art.flip_h and weapon.position == Vector2(-3, -8), "turning mirrors the hand without advancing the clock")
	check(is_equal_approx(weapon.rotation, -0.25) and weapon.scale.is_equal_approx(Vector2(-0.65, 0.65)), "weapon angle and scale reflect together")
	check(weapon.offset == Vector2(-8, -16) and not weapon.centered, "weapon rotates around its authored grip")
	check(art.offset == Vector2(0, -4), "body keeps its authored root instead of centering the silhouette")
	presenter.update("Active", 0.0, 1, 0.1, 0.0)
	check(art.frame == 5, "active begins on its first frame immediately")
	presenter.update("Dead", 0.0, 1)
	check(art.frame == 7 and not weapon.visible, "death clears equipment according to the same pose")
	actor.free()

# Keep a large boss atlas within GPU texture limits while retaining row-major clip indices.
func _test_grid_atlas() -> void:
	var actor := Node2D.new()
	root.add_child(actor)
	var definition := _fixture(Vector2i(16, 16), Vector2i(8, 12), {
		"Idle": {"start": 0, "count": 8, "fps": 8.0, "loop": true},
	}, 8, "sword")
	definition["columns"] = 4
	definition["rows"] = 2
	var art := _body(actor, definition)
	var presenter = load(HELPER).new(art, definition)
	presenter.update("Idle", 0.0, 1)
	presenter.update("Idle", 0.875, 1)
	check(art.hframes == 4 and art.vframes == 2 and art.frame == 7,
		"grid atlas preserves row-major frame indices across rows")
	actor.free()

# Catch a visual phase opening damage, frozen old poses and facing changes during a strike.
func _test_ground_phases() -> void:
	var definition := _fixture(Vector2i(128, 96), Vector2i(64, 72), {
		"Idle": {"start": 0, "count": 6, "fps": 6.0, "loop": true},
		"Walk": {"start": 6, "count": 12, "fps": 12.0, "loop": true},
		"Startup": {"start": 18, "count": 6, "fps": 12.0, "loop": false},
		"Active": {"start": 24, "count": 4, "fps": 12.0, "loop": false},
		"Recovery": {"start": 28, "count": 8, "fps": 12.0, "loop": false},
	}, 36, "sword")
	var enemy = load("res://Scenes/Enemies/GroundEnemy.tscn").instantiate()
	var art := _body(enemy, definition)
	root.add_child(enemy)
	enemy.set_physics_process(false)
	enemy.attack.set_physics_process(false)
	enemy._presentation = load(HELPER).new(art, definition)
	var shape: CollisionShape2D = enemy.get_node("CollisionShape2D")
	var hurt: CollisionShape2D = enemy.get_node("Hurtbox/CollisionShape2D")
	check(shape.shape.size.y == 60 and shape.position.y == -6 and hurt.position == shape.position,
		"custodian body and hurtbox grow upward while preserving floor at +24")
	enemy.facing = -1
	enemy._begin_attack()
	check(art.frame == 18 and enemy.attack.phase == MeleeAttack.Phase.STARTUP, "accepted strike immediately shows startup without opening damage")
	enemy.attack._physics_process(0.25)
	enemy._update_visual()
	check(art.frame == 21, "startup moves through real intermediate poses")
	enemy.facing = 1
	enemy.attack._physics_process(0.25)
	check(art.frame == 24 and art.flip_h and enemy.attack.phase == MeleeAttack.Phase.ACTIVE,
		"active pose follows damage authority and retains accepted facing")
	enemy.attack._physics_process(0.12)
	check(art.frame == 28 and enemy.attack.phase == MeleeAttack.Phase.RECOVERY, "recovery starts when the hitbox closes")
	enemy.attack.cancel()
	enemy._update_visual()
	check(art.frame < 18 and enemy.attack.phase == MeleeAttack.Phase.IDLE, "cancel returns to locomotion without a stale strike pose")
	enemy.free()
	await process_frame

# Catch timed caster/boss poses drifting from their state timer or changing collision support.
func _test_ranged_and_boss_states() -> void:
	var ranged_data := _fixture(Vector2i(96, 96), Vector2i(48, 72), {
		"Idle": {"start": 0, "count": 8, "fps": 6.0, "loop": true},
		"Tell": {"start": 8, "count": 8, "fps": 12.0, "loop": false},
		"Throw": {"start": 16, "count": 6, "fps": 12.0, "loop": false},
		"Recover": {"start": 22, "count": 8, "fps": 12.0, "loop": false},
	}, 30, "censer")
	var ranged = load("res://Scenes/Enemies/RangedEnemy.tscn").instantiate()
	var ranged_art := _body(ranged, ranged_data)
	root.add_child(ranged)
	ranged.set_physics_process(false)
	ranged._presentation = load(HELPER).new(ranged_art, ranged_data)
	var ranged_shape: CollisionShape2D = ranged.get_node("CollisionShape2D")
	check(ranged_shape.shape.size.y == 56 and ranged_shape.position.y == -4,
		"acolyte grows upward while preserving floor at +24")
	ranged._set_state(RangedEnemy.State.TELL, 0.6)
	ranged.timer = 0.3
	ranged._update_visual()
	check(ranged_art.frame == 12, "casting tell is sampled from its actual timer")
	ranged._set_state(RangedEnemy.State.THROW, 0.15)
	check(ranged_art.frame == 16, "throw enters its own clip immediately")
	ranged.free()

	var boss_data := _fixture(Vector2i(256, 160), Vector2i(128, 96), {
		"Idle": {"start": 0, "count": 8, "fps": 6.0, "loop": true},
		"Advance": {"start": 8, "count": 12, "fps": 12.0, "loop": true},
		"SweepTell": {"start": 20, "count": 8, "fps": 12.0, "loop": false},
		"Sweep": {"start": 28, "count": 6, "fps": 12.0, "loop": false},
		"SweepRecover": {"start": 34, "count": 10, "fps": 12.0, "loop": false},
		"RainTell": {"start": 44, "count": 8, "fps": 12.0, "loop": false},
		"Rain": {"start": 52, "count": 6, "fps": 12.0, "loop": false},
		"Exhausted": {"start": 58, "count": 10, "fps": 12.0, "loop": false},
		"Stagger": {"start": 68, "count": 8, "fps": 12.0, "loop": false},
		"Dead": {"start": 76, "count": 12, "fps": 12.0, "loop": false},
	}, 88, "scythe")
	var boss = load("res://Scenes/Bosses/Boss.tscn").instantiate()
	var boss_art := _body(boss, boss_data)
	root.add_child(boss)
	boss.set_physics_process(false)
	boss.attack.set_physics_process(false)
	boss._presentation = load(HELPER).new(boss_art, boss_data)
	var boss_shape: CollisionShape2D = boss.get_node("CollisionShape2D")
	check(boss_shape.shape.size.y == 88 and boss_shape.position.y == 12 and boss.attack.position.y == 44,
		"abbot shrinks to 88px without moving floor +56 or low attack origin")
	boss._enter(Boss.State.RAIN_TELL, 0.9)
	boss.timer = 0.45
	boss._update_visual()
	check(boss_art.frame == 48, "rain anticipation samples the state timer")
	boss._enter(Boss.State.EXHAUSTED, 1.6)
	check(boss_art.frame == 58, "exhaustion switches to its distinct recovery clip")
	boss._on_died(null)
	check(boss_art.frame == 76, "death begins its authored clip immediately")
	boss.free()
	await process_frame
