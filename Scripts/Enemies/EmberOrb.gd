class_name EmberOrb
extends Area2D

## Proyectil del acólito: avanza en línea recta a la altura del pecho. Daña una
## vez a la zona vulnerable del jugador (pasando por su Health, así que el Voto
## lo reduce) y desaparece al chocar con un muro o tras `lifetime`. Se esquiva
## saltando por encima.

const ART := "res://Sprites/Enemies/ember_orb.png"
const RADIUS := 5.0

var direction: float = 1.0
var speed: float = 150.0
var damage: float = 12.0
var source: Node2D
var lifetime: float = 3.0
var _sprite: Sprite2D
var _time: float = 0.0

func setup(from: Node2D, dir: float, orb_speed: float, orb_damage: float) -> EmberOrb:
	source = from
	direction = signf(dir)
	speed = orb_speed
	damage = orb_damage
	return self

func _ready() -> void:
	add_to_group(&"projectiles")
	collision_layer = 64 # enemy_hitbox
	collision_mask = 8 | 1 # player_hurtbox + mundo
	var shape := CircleShape2D.new()
	shape.radius = RADIUS
	var collision := CollisionShape2D.new()
	collision.shape = shape
	add_child(collision)
	if ResourceLoader.exists(ART):
		_sprite = Sprite2D.new()
		_sprite.texture = load(ART)
		_sprite.hframes = 2
		add_child(_sprite)
	area_entered.connect(_on_area_entered)
	# La capa 1 incluye también el cuerpo del jugador: sólo los muros la apagan.
	body_entered.connect(func(body: Node2D):
		if body is StaticBody2D:
			queue_free())

func _physics_process(delta: float) -> void:
	position.x += direction * speed * delta
	_time += delta
	if _sprite:
		_sprite.frame = int(_time * 10.0) % 2
		_sprite.flip_h = direction < 0.0
	if _time >= lifetime:
		queue_free()

func _on_area_entered(area: Area2D) -> void:
	var hurtbox := area as Hurtbox
	if hurtbox and not is_queued_for_deletion():
		hurtbox.receive_hit(damage, source if is_instance_valid(source) else self)
		queue_free()

func _draw() -> void:
	if _sprite:
		return
	draw_circle(Vector2.ZERO, RADIUS + 1.0, Color("b96a47"))
	draw_circle(Vector2.ZERO, RADIUS - 1.5, Color("ffd59a"))
