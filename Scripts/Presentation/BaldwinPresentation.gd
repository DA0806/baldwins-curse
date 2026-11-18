extends Node2D
## The body owns the visual clock; equipment follows each generated hand pose.

const BODY_DIRECTORY := "res://Sprites/Characters/Baldwin/"

var body: AnimatedSprite2D
var inventory: PlayerInventory
var pose_data: Dictionary
var weapon_sprite: Sprite2D
var displayed_weapon: WeaponData
var _locked_weapon: WeaponData
var _locked_texture: Texture2D
var _locked_family := "Sword"
var _locked_facing := 1

# Build full-cell atlases only when every generated sheet matches its pose contract.
static func load_frames(data: Dictionary) -> SpriteFrames:
	if data.is_empty():
		push_error("Baldwin presentation requires generated BaldwinPoseData.DATA and body-only sheets.")
		return null
	var frames := SpriteFrames.new()
	frames.remove_animation(&"default")
	for clip in data:
		var entry: Dictionary = data[clip]
		var count: int = int(entry.get("count", 0))
		var fps: float = float(entry.get("fps", 0.0))
		var poses: Array = entry.get("poses", [])
		var path := BODY_DIRECTORY + String(clip) + ".png"
		if count <= 0 or fps <= 0.0 or poses.size() != count or not ResourceLoader.exists(path):
			push_error("Missing or invalid generated Baldwin clip: %s" % clip)
			return null
		var texture := load(path) as Texture2D
		if not texture or texture.get_size() != Vector2(128 * count, 128):
			push_error("Baldwin clip %s must contain %d full 128x128 cells." % [clip, count])
			return null
		frames.add_animation(clip)
		frames.set_animation_speed(clip, fps)
		frames.set_animation_loop(clip, bool(entry.get("loop", false)))
		for index in count:
			var cell := AtlasTexture.new()
			cell.atlas = texture
			cell.region = Rect2(index * 128, 0, 128, 128)
			frames.add_frame(clip, cell)
	return frames

# Attach equipment to the existing player root without changing body collision or pivot.
func setup(sprite: AnimatedSprite2D, bag: PlayerInventory, data: Dictionary) -> void:
	body = sprite
	inventory = bag
	pose_data = data
	weapon_sprite = Sprite2D.new()
	weapon_sprite.name = "WeaponArt"
	weapon_sprite.offset = Vector2(24, 0) # 64x32 texture, grip at (8,16).
	weapon_sprite.z_index = 1
	add_child(weapon_sprite)
	body.frame_changed.connect(sync_pose)
	body.animation_changed.connect(sync_pose)
	inventory.weapon_swapped.connect(_on_weapon_swapped)
	refresh_inventory()

# Follow damage tint and the body's frame without introducing a second animation clock.
func _process(_delta: float) -> void:
	sync_pose()

# Retain the last accepted weapon while it is still carried; otherwise choose the first slot.
func refresh_inventory() -> void:
	if not inventory or _locked_weapon:
		return
	if not displayed_weapon or not inventory.weapons.has(displayed_weapon):
		displayed_weapon = null
		for weapon in inventory.weapons:
			if weapon:
				displayed_weapon = weapon
				break
	sync_pose()

# Defer visual inventory changes until an accepted attack completes or is interrupted.
func _on_weapon_swapped(_slot: int, _new_weapon: WeaponData, _old_weapon: WeaponData) -> void:
	refresh_inventory()

# Snapshot gesture, texture and facing before MeleeAttack emits its synchronous startup signal.
func begin_attack(weapon: WeaponData, facing: int) -> void:
	_locked_weapon = weapon
	displayed_weapon = weapon
	_locked_texture = weapon.equipped_texture
	_locked_family = "Mace" if weapon.combo_animation_tag == "mace" else "Sword"
	_locked_facing = facing

# Let the real combat phase choose its clip and duration, never the reverse.
func play_attack_phase(phase: int, spec: MeleeAttack.Spec) -> void:
	if not _locked_weapon:
		return
	var suffix := ""
	var duration := 0.0
	match phase:
		MeleeAttack.Phase.STARTUP:
			suffix = "Startup"
			duration = spec.startup
		MeleeAttack.Phase.ACTIVE:
			suffix = "Active"
			duration = spec.active
		MeleeAttack.Phase.RECOVERY:
			suffix = "Recovery"
			duration = spec.recovery
		_:
			return
	play_actor(StringName("Attack" + _locked_family + suffix), duration)

# Release the snapshot after cancellation or completion and reconcile carried equipment.
func end_attack() -> void:
	_locked_weapon = null
	_locked_texture = null
	refresh_inventory()

# Play body animation at its own cadence or fit a phase's frames to the combat duration.
func play_actor(clip: StringName, duration := 0.0) -> void:
	if not body or pose_data.is_empty():
		return
	if not body.sprite_frames.has_animation(clip):
		push_error("Baldwin body clip is not installed: %s" % clip)
		return
	var frames := body.sprite_frames
	body.speed_scale = frames.get_frame_count(clip) / (frames.get_animation_speed(clip) * duration) if duration > 0.0 else 1.0
	body.play(clip)
	body.set_frame_and_progress(0, 0.0)
	sync_pose()

# Reflect hand coordinates and rotation around the same root used by the full body cell.
func sync_pose() -> void:
	if not weapon_sprite or not body or not inventory:
		return
	var texture: Texture2D = _locked_texture if _locked_weapon else (displayed_weapon.equipped_texture if displayed_weapon else null)
	weapon_sprite.texture = texture
	var clip: Dictionary = pose_data.get(String(body.animation), {})
	var poses: Array = clip.get("poses", [])
	if poses.is_empty() or body.frame >= poses.size():
		weapon_sprite.hide()
		return
	var pose: Dictionary = poses[body.frame]
	var facing: int = _locked_facing if _locked_weapon else (-1 if body.flip_h else 1)
	body.flip_h = facing < 0
	body.offset.x = -32.0 if facing < 0 else 32.0
	var hand: Array = pose["hand"]
	weapon_sprite.position = Vector2(float(hand[0]) * facing, float(hand[1]))
	weapon_sprite.scale = Vector2(facing, 1)
	weapon_sprite.rotation = float(pose["angle"]) * facing
	weapon_sprite.modulate = body.modulate
	weapon_sprite.visible = texture != null and bool(pose.get("weapon_visible", true))
