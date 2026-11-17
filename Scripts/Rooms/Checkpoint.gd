extends Area2D

## Punto de control. Va dentro del nodo `Spawns` de la sala y su nombre es su
## spawn_id: al restaurarlo, el jugador aparece aquí. Cada entrada del jugador
## guarda el estado actual (la última activación es la que cuenta).

const SIZE := Vector2(24, 64)
const COLOR_POLE := Color("6d8297")
const COLOR_IDLE := Color("303b4a")
const COLOR_ACTIVE := Color("f0a758")

## Hijo opcional "Art" (Sprite2D, 4 cuadros: apagado + 3 de llama).
@onready var art: Sprite2D = get_node_or_null("Art") as Sprite2D
var _flame_time: float = 0.0

func _process(delta: float) -> void:
	if not art:
		return
	if is_active():
		_flame_time += delta
		art.frame = 1 + int(_flame_time * 8.0) % 3
	else:
		art.frame = 0

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2 # player
	var shape := RectangleShape2D.new()
	shape.size = SIZE
	var collision := CollisionShape2D.new()
	collision.shape = shape
	add_child(collision)
	body_entered.connect(_on_body_entered)
	RunSession.of(self).checkpoint_activated.connect(func(_room: String, _spawn: String): queue_redraw())

func is_active() -> bool:
	return RunSession.of(self).is_active_checkpoint(owner.room_id, name)

func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		var was_active: bool = is_active()
		RunSession.of(self).activate_checkpoint(owner, body, name)
		if not was_active and is_active():
			SoundBank.play(self, &"checkpoint")

## Poste con llama: apagada (piedra) o encendida (brasa). La forma de la
## llama crece al activarse para que se lea también sin color.
func _draw() -> void:
	if art:
		return
	draw_rect(Rect2(-2, -20, 4, 52), COLOR_POLE)
	var active: bool = is_active()
	var height: float = 18.0 if active else 8.0
	draw_colored_polygon(PackedVector2Array([
		Vector2(-7, -20), Vector2(7, -20), Vector2(0, -20 - height)
	]), COLOR_ACTIVE if active else COLOR_IDLE)
