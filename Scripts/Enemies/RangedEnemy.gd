class_name RangedEnemy
extends CharacterBody2D

## Acólito de la Ascua: enemigo a distancia. Mira al jugador cuando lo detecta,
## anticipa cada lanzamiento (incensario alzado, color de brasa, "!") durante
## `tell_time` y lanza una brasa en línea recta. Se puede saltar la brasa o
## acercarse y golpearlo durante la recuperación.

enum State { IDLE, TELL, THROW, RECOVER, DEAD }

const COLOR_IDLE := Color(0.478, 0.227, 0.133) # cobre oscuro
const COLOR_TELL := Color(0.94, 0.65, 0.35)    # brasa
const COLOR_RECOVER := Color(0.3, 0.16, 0.12)

signal threw(orb: EmberOrb)

@export var detect_range: float = 300.0
@export var detect_height: float = 90.0
@export var tell_time: float = 0.6
@export var throw_time: float = 0.15
@export var recover_time: float = 0.7
@export var cooldown: float = 1.4
@export var projectile_damage: float = 12.0
@export var projectile_speed: float = 150.0
## Punto de salida de la brasa respecto al centro, mirando a la derecha.
@export var spawn_offset: Vector2 = Vector2(14, -8)
@export var gravity: float = 980.0

var state: State = State.IDLE
var facing: int = -1
var timer: float = 0.0
var cooldown_left: float = 0.0
var home: Vector2

@onready var health: Health = $Health
@onready var hurtbox: Hurtbox = $Hurtbox
@onready var body: ColorRect = $Body
@onready var alert: Label = $Alert
## Hijo opcional "Art" (Sprite2D, 4 cuadros: reposo, anticipación, lanzamiento, recuperación).
@onready var art: Sprite2D = get_node_or_null("Art") as Sprite2D

func _ready() -> void:
	add_to_group(&"enemies")
	add_to_group(&"encounter")
	home = global_position
	health.died.connect(_on_died)
	health.damaged.connect(func(_amount: float, _source: Node):
		modulate = GameSettings.flash_color()
		create_tween().tween_property(self, "modulate", Color.WHITE, 0.15))
	_update_visual()

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	velocity.x = 0.0
	move_and_slide()
	if state == State.DEAD:
		return
	cooldown_left = maxf(0.0, cooldown_left - delta)
	timer -= delta
	match state:
		State.IDLE:
			var player := _find_player()
			if player:
				facing = 1 if player.global_position.x > global_position.x else -1
				if cooldown_left <= 0.0:
					_set_state(State.TELL, tell_time)
		State.TELL:
			if timer <= 0.0:
				_throw()
				_set_state(State.THROW, throw_time)
		State.THROW:
			if timer <= 0.0:
				_set_state(State.RECOVER, recover_time)
		State.RECOVER:
			if timer <= 0.0:
				cooldown_left = cooldown
				_set_state(State.IDLE, 0.0)

func _set_state(new_state: State, duration: float) -> void:
	state = new_state
	timer = duration
	_update_visual()

func _throw() -> void:
	var orb := EmberOrb.new().setup(self, facing, projectile_speed, projectile_damage)
	orb.position = global_position + Vector2(spawn_offset.x * facing, spawn_offset.y)
	get_parent().add_child(orb)
	SoundBank.play(self, &"throw")
	threw.emit(orb)

func _find_player() -> Node2D:
	var player := get_tree().get_first_node_in_group("player") as Node2D
	if not player:
		return null
	var player_health := player.get_node_or_null("Health") as Health
	if player_health and player_health.is_dead():
		return null
	var offset: Vector2 = player.global_position - global_position
	if absf(offset.x) > detect_range or absf(offset.y) > detect_height:
		return null
	return player

func _on_died(_source: Node) -> void:
	_set_state(State.DEAD, 0.0)
	hurtbox.set_enabled(false)
	hide()

## Laboratorio: vuelve al estado inicial (en la campaña la sala se recarga).
func reset_encounter() -> void:
	health.reset()
	hurtbox.set_enabled(true)
	global_position = home
	cooldown_left = 0.0
	modulate = Color.WHITE
	show()
	_set_state(State.IDLE, 0.0)

func _update_visual() -> void:
	alert.visible = state == State.TELL
	if art:
		body.visible = false
		art.flip_h = facing < 0
		art.frame = {State.TELL: 1, State.THROW: 2, State.RECOVER: 3}.get(state, 0)
		return
	match state:
		State.TELL, State.THROW:
			body.color = COLOR_TELL
		State.RECOVER:
			body.color = COLOR_RECOVER
		_:
			body.color = COLOR_IDLE
