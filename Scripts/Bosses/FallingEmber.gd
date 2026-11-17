class_name FallingEmber
extends Area2D

## Brasa de la lluvia del Abad. Primero marca en el suelo dónde caerá durante
## `warn_time` (sin poder dañar); después cae, daña una vez al jugador que toque
## (pasando por su Health) y se apaga contra el suelo.

const ART := "res://Sprites/Bosses/falling_ember.png"
const MARKER_ART := "res://Sprites/Bosses/ember_marker.png"
const FALL_HEIGHT := 260.0
const SIZE := Vector2(12, 20)

signal landed

var floor_y: float = 256.0
var warn_time: float = 0.9
var fall_speed: float = 420.0
var damage: float = 20.0
var source: Node2D
var falling: bool = false

var _visual: Node2D
var _marker: Node2D
var _time: float = 0.0

func setup(from: Node2D, x: float, ground_y: float, warn: float, ember_damage: float) -> FallingEmber:
	source = from
	floor_y = ground_y
	warn_time = warn
	damage = ember_damage
	position = Vector2(x, ground_y - FALL_HEIGHT)
	return self

func _ready() -> void:
	add_to_group(&"boss_embers")
	collision_layer = 64 # enemy_hitbox
	collision_mask = 8   # player_hurtbox
	monitoring = false
	var shape := RectangleShape2D.new()
	shape.size = SIZE
	var collision := CollisionShape2D.new()
	collision.shape = shape
	add_child(collision)
	area_entered.connect(_on_area_entered)
	# Marca en el suelo: independiente de la caída (top_level).
	_marker = _make_visual(MARKER_ART, 1, Vector2(32, 4), Color(0.94, 0.65, 0.35, 0.8))
	_marker.top_level = true
	add_child(_marker)
	_marker.global_position = Vector2(position.x, floor_y - 3.0)
	_visual = _make_visual(ART, 2, SIZE, Color(1.0, 0.835, 0.604))
	_visual.visible = false
	add_child(_visual)

## Sprite si el arte existe; si no, un rectángulo provisional centrado.
func _make_visual(path: String, frames: int, size: Vector2, color: Color) -> Node2D:
	if ResourceLoader.exists(path):
		var sprite := Sprite2D.new()
		sprite.texture = load(path)
		sprite.hframes = frames
		return sprite
	var holder := Node2D.new()
	var rect := ColorRect.new()
	rect.size = size
	rect.position = -size / 2.0
	rect.color = color
	holder.add_child(rect)
	return holder

func _physics_process(delta: float) -> void:
	_time += delta
	if not falling:
		warn_time -= delta
		# Aviso que parpadea; con efectos reducidos queda fijo.
		_marker.modulate.a = 0.9 if GameSettings.reduced_effects else 0.55 + 0.45 * absf(sin(_time * 10.0))
		if warn_time <= 0.0:
			falling = true
			_visual.visible = true
			set_deferred("monitoring", true)
		return
	position.y += fall_speed * delta
	if _visual is Sprite2D:
		(_visual as Sprite2D).frame = int(_time * 12.0) % 2
	if position.y >= floor_y - SIZE.y / 2.0:
		SoundBank.play(self, &"ember_impact")
		landed.emit()
		queue_free()

func _on_area_entered(area: Area2D) -> void:
	var hurtbox := area as Hurtbox
	if hurtbox and falling and not is_queued_for_deletion():
		hurtbox.receive_hit(damage, source if is_instance_valid(source) else self)
		queue_free()
