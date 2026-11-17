class_name GroundEnemy
extends CharacterBody2D

## Enemigo terrestre: patrulla alrededor de su punto de origen, detecta al
## jugador, se acerca, anticipa un golpe, ataca y se recupera.

enum State { PATROL, CHASE, ATTACK, DEAD }

@export_group("Movimiento")
@export var patrol_speed: float = 40.0
@export var chase_speed: float = 70.0
## Distancia máxima al punto de origen, tanto al patrullar como al perseguir.
@export var patrol_distance: float = 140.0
@export var gravity: float = 980.0

## Salud máxima de esta instancia. 0 = la del nodo Health de la escena.
@export var max_health_override: float = 0.0

@export_group("Detección")
@export var detect_range: float = 150.0
@export var detect_height: float = 80.0
@export var attack_range: float = 34.0

@export_group("Golpe")
@export var attack_damage: float = 15.0
@export var attack_reach: float = 42.0
@export var attack_height: float = 32.0
## Anticipación visible antes de que el golpe haga daño.
@export var attack_startup: float = 0.5
@export var attack_active: float = 0.12
@export var attack_recovery: float = 0.6
@export var attack_cooldown: float = 1.4

const COLOR_IDLE := Color(0.42, 0.16, 0.2)
const COLOR_TELEGRAPH := Color(0.94, 0.65, 0.35) # brasa
const COLOR_RECOVERY := Color(0.26, 0.12, 0.16)

var state: State = State.PATROL
var facing: int = -1
var home: Vector2

@onready var health: Health = $Health
@onready var hurtbox: Hurtbox = $Hurtbox
@onready var attack: MeleeAttack = $MeleeAttack
@onready var body: ColorRect = $Body
@onready var eye: ColorRect = $Eye
@onready var blade: ColorRect = $Blade
@onready var alert: Label = $Alert
## Hijo opcional "Art" (Sprite2D, 4 poses: reposo, anticipación, golpe, recuperación).
@onready var art: Sprite2D = get_node_or_null("Art") as Sprite2D

func _ready() -> void:
	add_to_group(&"enemies")
	add_to_group(&"encounter")
	home = global_position
	if max_health_override > 0.0:
		health.max_health = max_health_override
		health.current = max_health_override
	health.damaged.connect(_on_damaged)
	health.died.connect(_on_died)
	attack.phase_changed.connect(_on_attack_phase_changed)
	attack.finished.connect(_on_attack_finished)
	_update_visual()

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	velocity.x = 0.0
	match state:
		State.PATROL:
			if _find_player():
				state = State.CHASE
			else:
				if is_on_wall() or (global_position.x - home.x) * facing >= patrol_distance:
					facing = -facing
				velocity.x = facing * patrol_speed
		State.CHASE:
			var player := _find_player()
			if not player:
				state = State.PATROL
			else:
				var dx: float = player.global_position.x - global_position.x
				if dx != 0.0:
					facing = 1 if dx > 0.0 else -1
				if absf(dx) <= attack_range:
					_begin_attack()
				elif (global_position.x - home.x) * facing < patrol_distance:
					velocity.x = facing * chase_speed
	move_and_slide()
	_update_visual()

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

func _begin_attack() -> void:
	var spec := MeleeAttack.Spec.new()
	spec.damage = attack_damage
	spec.reach = attack_reach
	spec.height = attack_height
	spec.startup = attack_startup
	spec.active = attack_active
	spec.recovery = attack_recovery
	spec.cooldown = attack_cooldown
	spec.facing = facing
	if attack.start(spec):
		state = State.ATTACK

func _on_attack_phase_changed(_phase: int) -> void:
	_update_visual()

func _on_attack_finished(_interrupted: bool) -> void:
	if state == State.ATTACK:
		state = State.CHASE

func _on_damaged(_amount: float, _source: Node) -> void:
	modulate = GameSettings.flash_color()
	create_tween().tween_property(self, "modulate", Color.WHITE, 0.15)

func _on_died(_source: Node) -> void:
	state = State.DEAD
	attack.cancel()
	hurtbox.set_enabled(false)
	hide()

## Devuelve al enemigo a su estado inicial (reintento del jugador).
func reset_encounter() -> void:
	attack.cancel()
	attack.cooldown_left = 0.0
	health.reset()
	hurtbox.set_enabled(true)
	global_position = home
	velocity = Vector2.ZERO
	facing = -1
	state = State.PATROL
	modulate = Color.WHITE
	show()
	_update_visual()

## La anticipación se lee por color, por el signo "!" y por la hoja que se
## levanta; la hoja extendida marca la ventana activa.
func _update_visual() -> void:
	var phase: int = attack.phase
	var attack_facing: int = attack.spec.facing if phase != MeleeAttack.Phase.IDLE else facing
	eye.position.x = 4.0 if attack_facing > 0 else -10.0
	alert.visible = phase == MeleeAttack.Phase.STARTUP
	if art:
		body.visible = false
		eye.visible = false
		blade.visible = false
		art.flip_h = attack_facing < 0
		match phase:
			MeleeAttack.Phase.STARTUP: art.frame = 1
			MeleeAttack.Phase.ACTIVE: art.frame = 2
			MeleeAttack.Phase.RECOVERY: art.frame = 3
			_: art.frame = 0
		return
	blade.visible = phase == MeleeAttack.Phase.STARTUP or phase == MeleeAttack.Phase.ACTIVE
	match phase:
		MeleeAttack.Phase.STARTUP:
			body.color = COLOR_TELEGRAPH
			blade.size = Vector2(6.0, 26.0) # hoja levantada
			blade.position = Vector2(attack_facing * 12.0 - 3.0, -38.0)
		MeleeAttack.Phase.ACTIVE:
			body.color = Color.WHITE
			var near: float = attack.spec.near
			blade.size = Vector2(attack.spec.reach - near, 6.0) # hoja extendida = zona de golpe
			blade.position = Vector2(near if attack_facing > 0 else -attack.spec.reach, -3.0)
		MeleeAttack.Phase.RECOVERY:
			body.color = COLOR_RECOVERY
		_:
			body.color = COLOR_IDLE
