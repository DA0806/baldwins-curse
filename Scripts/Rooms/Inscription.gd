extends Area2D

## Inscripción en el muro: una placa que muestra su texto mientras el jugador
## está cerca. Cuenta la historia de Baldwin sin detener el juego.

const ART := "res://Sprites/Environment/Common/inscription.png"
const AREA := Vector2(96, 64)

@export_multiline var text: String = ""
@export var panel_width: float = 260.0

var _label: Label

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2 # player
	var shape := RectangleShape2D.new()
	shape.size = AREA
	var collision := CollisionShape2D.new()
	collision.shape = shape
	add_child(collision)
	# Placa a la altura de la cabeza, sobre el muro.
	if ResourceLoader.exists(ART):
		var plaque := Sprite2D.new()
		plaque.texture = load(ART)
		plaque.position = Vector2(0, -44)
		plaque.z_index = -1
		add_child(plaque)
	_label = Label.new()
	_label.text = text
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.size = Vector2(panel_width, 0)
	_label.position = Vector2(-panel_width / 2.0, -112)
	_label.add_theme_font_size_override("font_size", 10)
	_label.z_index = 10
	_label.visible = false
	add_child(_label)
	body_entered.connect(func(body: Node2D): _show(body, true))
	body_exited.connect(func(body: Node2D): _show(body, false))

func is_showing() -> bool:
	return _label.visible

func _show(body: Node2D, value: bool) -> void:
	if body.is_in_group("player"):
		_label.visible = value

func _draw() -> void:
	if ResourceLoader.exists(ART):
		return
	draw_rect(Rect2(-16, -56, 32, 24), Color("303b4a"))
	draw_rect(Rect2(-16, -56, 32, 24), Color("a99c80"), false, 1.0)
