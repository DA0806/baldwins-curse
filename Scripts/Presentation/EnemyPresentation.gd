class_name EnemyPresentation
extends RefCounted
## One pose clock drives the enemy body and its independently equipped weapon.

const DATA_PATH := "res://Scripts/Presentation/EnemyPoseData.gd"
const EQUIPMENT := {
	"sword": {"path": "res://Sprites/Equipment/sword.png", "grip": Vector2(8, 16)},
	"mace": {"path": "res://Sprites/Equipment/mace.png", "grip": Vector2(8, 16)},
	"scythe": {"path": "res://Sprites/Equipment/scythe.png", "grip": Vector2(16, 32)},
	"censer": {"path": "res://Sprites/Equipment/censer.png", "grip": Vector2(24, 8)},
}

var body: Sprite2D
var weapon: Sprite2D
var definition: Dictionary
var current_clip := ""
var elapsed := 0.0
var _textures: Dictionary = {}

# Resolve the generated actor definition without requiring unfinished art at parse time.
static func for_actor(art: Sprite2D, actor: String) -> EnemyPresentation:
	if not art or not ResourceLoader.exists(DATA_PATH):
		return null
	var source := load(DATA_PATH) as GDScript
	var data: Dictionary = source.get_script_constant_map().get("DATA", {})
	if not data.has(actor):
		return null
	return EnemyPresentation.new(art, data[actor])

# Keep the authored root and create equipment as a sibling, inheriting actor flashes.
func _init(art: Sprite2D, pose_definition: Dictionary) -> void:
	body = art
	definition = pose_definition
	var cell: Array = definition.cell
	var origin: Array = definition.root
	body.hframes = int(definition.get("columns", definition.poses.size()))
	body.vframes = int(definition.get("rows", 1))
	body.centered = true
	body.offset = Vector2(float(cell[0]) * 0.5 - float(origin[0]), float(cell[1]) * 0.5 - float(origin[1]))
	weapon = body.get_parent().get_node_or_null("WeaponArt") as Sprite2D
	if not weapon:
		weapon = Sprite2D.new()
		weapon.name = "WeaponArt"
		body.get_parent().add_child(weapon)
	weapon.z_index = body.z_index + 1
	weapon.centered = false
	weapon.visible = false

# Sample finite phases from their authority's progress, or loop locomotion on one clock.
func update(clip: String, delta: float, facing: int, duration: float = -1.0, phase_progress: float = -1.0) -> void:
	var clips: Dictionary = definition.clips
	if not clips.has(clip):
		clip = "Idle"
	if not clips.has(clip):
		weapon.visible = false
		return
	if current_clip != clip:
		current_clip = clip
		elapsed = 0.0
	else:
		elapsed += maxf(delta, 0.0)
	var sequence: Dictionary = clips[clip]
	var count: int = int(sequence.count)
	if count <= 0:
		weapon.visible = false
		return
	var index: int
	if phase_progress >= 0.0:
		index = mini(count - 1, floori(clampf(phase_progress, 0.0, 1.0) * count))
	elif duration > 0.0:
		index = mini(count - 1, floori(elapsed / duration * count))
	else:
		index = floori(elapsed * float(sequence.get("fps", 8.0)))
		index = index % count if sequence.get("loop", false) else mini(index, count - 1)
	body.frame = int(sequence.start) + index
	body.flip_h = facing < 0
	_apply_equipment(definition.poses[body.frame], facing)

# Reflect hand, angle and local weapon geometry together around the actor's root.
func _apply_equipment(pose: Dictionary, facing: int) -> void:
	var key: String = str(pose.get("weapon", ""))
	weapon.visible = bool(pose.get("weapon_visible", true)) and EQUIPMENT.has(key)
	if not weapon.visible:
		return
	var item: Dictionary = EQUIPMENT[key]
	if not _textures.has(key):
		_textures[key] = load(item.path) if ResourceLoader.exists(item.path) else null
	weapon.texture = _textures[key]
	var hand: Array = pose.hand
	weapon.position = Vector2(float(hand[0]) * facing, float(hand[1]))
	weapon.rotation = float(pose.get("angle", 0.0)) * facing
	var size: float = float(pose.get("weapon_scale", 1.0))
	weapon.scale = Vector2(size * facing, size)
	weapon.offset = -Vector2(item.grip)
