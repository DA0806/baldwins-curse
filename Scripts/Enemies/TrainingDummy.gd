class_name TrainingDummy
extends Node2D

## Maniquí instrumentado: registra cada golpe recibido y nunca muere.

## Un registro por golpe: {"damage": float, "frame": int (tick de física)}.
var hit_log: Array[Dictionary] = []

@onready var health: Health = $Health
@onready var body: ColorRect = $Body
@onready var label: Label = $Label

func _ready() -> void:
	add_to_group(&"encounter")
	health.damaged.connect(_on_damaged)
	health.died.connect(func(_source: Node): health.reset.call_deferred())
	_refresh()

func total_damage() -> float:
	var total: float = 0.0
	for hit in hit_log:
		total += hit.damage
	return total

func reset_encounter() -> void:
	hit_log.clear()
	health.reset()
	_refresh()

func _on_damaged(amount: float, _source: Node) -> void:
	hit_log.append({"damage": amount, "frame": Engine.get_physics_frames()})
	body.modulate = GameSettings.flash_color()
	create_tween().tween_property(body, "modulate", Color.WHITE, 0.15)
	_refresh()

func _refresh() -> void:
	if hit_log.is_empty():
		label.text = "maniquí"
	else:
		label.text = "%d · último %d" % [hit_log.size(), hit_log.back().damage]
