class_name Hitbox
extends Area2D

## Zona de golpe. Sólo existe mientras un ataque la abre; golpea a cada
## objetivo (cada Health) como máximo una vez por apertura.

signal hit_landed(target: Hurtbox, damage: float)

const GROUP: StringName = &"hitboxes"

## Dibuja las zonas de golpe y vulnerables. Activo en builds de depuración.
static var debug_draw: bool = false # F3 lo alterna en builds de depuración (GameSession)

var active: bool = false

var _damage: float = 0.0
var _already_hit: Dictionary = {}
var _rect := RectangleShape2D.new()
var _shape := CollisionShape2D.new()

## Si la Hitbox se libera sin haber entrado al árbol, su forma nunca tuvo padre.
func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE and is_instance_valid(_shape) and not _shape.get_parent():
		_shape.free()

func _ready() -> void:
	add_to_group(GROUP)
	monitorable = false
	_shape.shape = _rect
	_shape.disabled = true
	add_child(_shape)
	area_entered.connect(_try_hit)

## Abre la zona delante del atacante: de `near` a `reach` píxeles desde su
## origen, hacia `facing` (1 derecha, -1 izquierda).
func open(damage: float, near: float, reach: float, height: float, facing: int) -> void:
	_already_hit.clear()
	_damage = damage
	_rect.size = Vector2(reach - near, height)
	_shape.position = Vector2(facing * (near + reach) / 2.0, 0.0)
	_shape.disabled = false
	active = true
	queue_redraw()

func close() -> void:
	if not active:
		return
	active = false
	_shape.set_deferred("disabled", true)
	queue_redraw()

## Rectángulo actual en coordenadas de mundo (para pruebas y depuración).
func get_world_rect() -> Rect2:
	return Rect2(_shape.global_position - _rect.size / 2.0, _rect.size)

func _physics_process(_delta: float) -> void:
	if active:
		for area in get_overlapping_areas():
			_try_hit(area)

func _try_hit(area: Area2D) -> void:
	var target := area as Hurtbox
	if not active or not target:
		return
	# Un personaje con varias zonas vulnerables cuenta como un solo objetivo.
	var key: int = target.health.get_instance_id() if target.health else target.get_instance_id()
	if _already_hit.has(key):
		return
	_already_hit[key] = true
	hit_landed.emit(target, target.receive_hit(_damage, owner))

func _draw() -> void:
	if debug_draw and active:
		var rect := Rect2(_shape.position - _rect.size / 2.0, _rect.size)
		draw_rect(rect, Color(1.0, 0.25, 0.2, 0.35))
		draw_rect(rect, Color(1.0, 0.25, 0.2, 0.9), false, 1.0)
