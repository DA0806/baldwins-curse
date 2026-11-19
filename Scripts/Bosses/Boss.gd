class_name Boss
extends CharacterBody2D

## El Abad Sellado. Dos patrones con anticipación distinta en forma, ritmo y
## sonido, cada uno seguido de una ventana de vulnerabilidad:
##
## · Tajo bajo: se acerca, echa la guadaña atrás (0,8 s, "!", chirrido) y barre
##   a ras de suelo 104 px. Se esquiva saltando. Al terminar queda con la
##   guadaña clavada: vulnerable 1,3 s.
## · Lluvia de ascuas: alza el incensario (0,9 s, tañido) y marca en el suelo
##   dónde caerán 3 brasas, separadas 80 px y centradas en el jugador. Los huecos
##   entre marcas son seguros. Después queda agotado: vulnerable 1,6 s.
##
## Sólo recibe daño en esas ventanas: su zona vulnerable está apagada el resto
## del tiempo y el sello del pecho brilla mientras dura. Al bajar a la mitad de
## salud ruge (1,2 s, invulnerable) y pasa a la fase 2: anticipaciones un 25 %
## más cortas, dos tajos por cada lluvia y lluvias de 5 brasas a 64 px.
## Usa el mismo contrato de daño que los demás enemigos (Health, Hurtbox,
## MeleeAttack), así que el Voto y el Ascua le afectan igual.

enum State { DORMANT, ADVANCE, SWEEP_TELL, SWEEP, SWEEP_RECOVER, RAIN_TELL, RAIN, EXHAUSTED, STAGGER, DEAD }

const PATTERNS: Dictionary = {1: [&"sweep", &"rain"], 2: [&"sweep", &"sweep", &"rain"]}
## Fase -> [número de brasas, separación].
const RAIN_LAYOUT: Dictionary = {1: [3, 80.0], 2: [5, 64.0]}
const FRAMES: Dictionary = {
	State.SWEEP_TELL: 1, State.SWEEP: 2, State.SWEEP_RECOVER: 3, State.RAIN_TELL: 4,
	State.RAIN: 5, State.EXHAUSTED: 6, State.STAGGER: 7, State.DEAD: 8,
}
const PRESENTATION = preload("res://Scripts/Presentation/EnemyPresentation.gd")

signal woke
signal pattern_started(pattern: StringName)
signal vulnerable_changed(is_vulnerable: bool)
signal phase_changed(new_phase: int)
signal defeated

@export_group("Comportamiento")
@export var wake_distance: float = 280.0
@export var walk_speed: float = 60.0
@export var sweep_trigger_distance: float = 84.0
@export var arena_left: float = 40.0
@export var arena_right: float = 920.0
@export var floor_y: float = 256.0
@export var gravity: float = 980.0

@export_group("Tajo")
@export var sweep_tell: float = 0.8
@export var sweep_active: float = 0.15
@export var sweep_recover: float = 1.3
@export var sweep_damage: float = 25.0
@export var sweep_reach: float = 104.0
@export var sweep_height: float = 24.0

@export_group("Lluvia")
@export var rain_tell: float = 0.9
@export var rain_damage: float = 20.0
## Tiempo desde el fin de la anticipación hasta que todas las brasas han caído.
@export var rain_fall_time: float = 0.75
@export var exhausted_time: float = 1.6

@export_group("Fase 2")
@export var stagger_time: float = 1.2
@export var phase2_tell_scale: float = 0.75

var state: State = State.DORMANT
var phase: int = 1
var facing: int = -1
var timer: float = 0.0
var pattern_index: int = 0
var current_pattern: StringName = &""
var rain_targets: Array[float] = []
var vulnerable: bool = false
var _presentation
var _state_duration := 0.0

@onready var health: Health = $Health
@onready var hurtbox: Hurtbox = $Hurtbox
@onready var attack: MeleeAttack = $MeleeAttack
@onready var body: ColorRect = $Body
@onready var seal: ColorRect = $Seal
@onready var scythe: ColorRect = $Scythe
@onready var censer: ColorRect = $Censer
@onready var alert: Label = $Alert
@onready var bar_layer: CanvasLayer = $BossBar
@onready var bar: ProgressBar = $BossBar/Bar
## Optional animated body atlas; the scythe/censer is a separate synchronized layer.
@onready var art: Sprite2D = get_node_or_null("Art") as Sprite2D

func _ready() -> void:
	add_to_group(&"enemies")
	add_to_group(&"bosses")
	health.died.connect(_on_died)
	health.damaged.connect(_on_damaged)
	health.health_changed.connect(func(current: float, maximum: float):
		bar.max_value = maximum
		bar.value = current)
	attack.phase_changed.connect(_on_attack_phase)
	attack.finished.connect(_on_attack_finished)
	bar.max_value = health.max_health
	bar.value = health.current
	bar_layer.visible = false
	_presentation = PRESENTATION.for_actor(art, "abad")
	_set_vulnerable(false)
	_update_visual()

func tell(base: float) -> float:
	return base * (phase2_tell_scale if phase == 2 else 1.0)

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	velocity.x = 0.0
	timer -= delta
	var player := _find_player()
	match state:
		State.DORMANT:
			if player and absf(player.global_position.x - global_position.x) <= wake_distance:
				bar_layer.visible = true
				woke.emit()
				SoundBank.play(self, &"roar")
				_enter(State.STAGGER, stagger_time)
		State.ADVANCE:
			if player:
				_think(player)
		State.RAIN_TELL:
			if timer <= 0.0:
				_enter(State.RAIN, rain_fall_time)
		State.RAIN:
			if timer <= 0.0:
				_set_vulnerable(true)
				_enter(State.EXHAUSTED, exhausted_time)
		State.EXHAUSTED:
			if timer <= 0.0:
				_set_vulnerable(false)
				_finish_pattern()
		State.STAGGER:
			if timer <= 0.0:
				_enter(State.ADVANCE, 0.0)
	move_and_slide()
	_update_visual(delta)

func _think(player: Node2D) -> void:
	var dx: float = player.global_position.x - global_position.x
	facing = 1 if dx > 0.0 else -1
	if current_pattern == &"":
		var list: Array = PATTERNS[phase]
		current_pattern = list[pattern_index % list.size()]
		pattern_index += 1
		pattern_started.emit(current_pattern)
	if current_pattern == &"rain":
		_start_rain(player)
	elif absf(dx) <= sweep_trigger_distance:
		_start_sweep()
	else:
		velocity.x = facing * walk_speed

func _start_sweep() -> void:
	var spec := MeleeAttack.Spec.new()
	spec.damage = sweep_damage
	spec.near = 0.0
	spec.reach = sweep_reach
	spec.height = sweep_height
	spec.startup = tell(sweep_tell)
	spec.active = sweep_active
	spec.recovery = sweep_recover
	spec.cooldown = 0.0
	spec.facing = facing
	if attack.start(spec):
		SoundBank.play(self, &"tell_sweep")

func _start_rain(player: Node2D) -> void:
	var layout: Array = RAIN_LAYOUT[phase]
	var count: int = layout[0]
	var spacing: float = layout[1]
	var half_span: float = spacing * (count - 1) / 2.0
	var center: float = clampf(player.global_position.x, arena_left + half_span, arena_right - half_span)
	rain_targets.clear()
	var warn: float = tell(rain_tell)
	for i in count:
		var x: float = center + (i - (count - 1) / 2.0) * spacing
		rain_targets.append(x)
		get_parent().add_child(FallingEmber.new().setup(self, x, floor_y, warn, rain_damage))
	SoundBank.play(self, &"tell_rain")
	_enter(State.RAIN_TELL, warn)

func _finish_pattern() -> void:
	current_pattern = &""
	_enter(State.ADVANCE, 0.0)

func _enter(new_state: State, duration: float) -> void:
	state = new_state
	timer = duration
	_state_duration = duration
	_update_visual()

func _on_attack_phase(attack_phase: int) -> void:
	match attack_phase:
		MeleeAttack.Phase.STARTUP:
			_enter(State.SWEEP_TELL, 0.0)
		MeleeAttack.Phase.ACTIVE:
			_enter(State.SWEEP, 0.0)
		MeleeAttack.Phase.RECOVERY:
			_set_vulnerable(true)
			_enter(State.SWEEP_RECOVER, 0.0)

func _on_attack_finished(interrupted: bool) -> void:
	_set_vulnerable(false)
	if not interrupted and state == State.SWEEP_RECOVER:
		_finish_pattern()

func _on_damaged(_amount: float, _source: Node) -> void:
	modulate = GameSettings.flash_color()
	create_tween().tween_property(self, "modulate", Color.WHITE, 0.12)
	if phase == 1 and not health.is_dead() and health.current <= health.max_health * 0.5:
		_enter_phase_two()

## Transición de fase reconocible: rugido, sello partido, 1,2 s sin daño.
func _enter_phase_two() -> void:
	phase = 2
	_enter(State.STAGGER, stagger_time)
	attack.cancel()
	_set_vulnerable(false)
	pattern_index = 0
	current_pattern = &""
	SoundBank.play(self, &"roar")
	phase_changed.emit(phase)

func _on_died(_source: Node) -> void:
	_enter(State.DEAD, 0.0)
	attack.cancel()
	_set_vulnerable(false)
	collision_layer = 0
	get_tree().call_group(&"boss_embers", "queue_free")
	bar_layer.visible = false
	defeated.emit()

func _set_vulnerable(value: bool) -> void:
	vulnerable = value
	hurtbox.set_enabled(value)
	vulnerable_changed.emit(value)

func _find_player() -> Node2D:
	var player := get_tree().get_first_node_in_group("player") as Node2D
	if not player:
		return null
	var player_health := player.get_node_or_null("Health") as Health
	if player_health and player_health.is_dead():
		return null
	return player

## Forma antes que color: guadaña alzada (tajo) frente a incensario en alto
## (lluvia), cuerpo arrodillado y sello encendido cuando es vulnerable.
func _update_visual(delta: float = 0.0) -> void:
	alert.visible = state == State.SWEEP_TELL
	if art:
		for node in [body, seal, scythe, censer]:
			node.visible = false
		if _presentation:
			var clip: String = {
				State.SWEEP_TELL: "SweepTell", State.SWEEP: "Sweep", State.SWEEP_RECOVER: "SweepRecover",
				State.RAIN_TELL: "RainTell", State.RAIN: "Rain", State.EXHAUSTED: "Exhausted",
				State.STAGGER: "Stagger", State.DEAD: "Dead",
			}.get(state, "Advance" if absf(velocity.x) > 0.1 and state == State.ADVANCE else "Idle")
			var duration := _state_duration
			var progress := 1.0 - timer / duration if duration > 0.0 else -1.0
			var visual_facing := facing
			if state in [State.SWEEP_TELL, State.SWEEP, State.SWEEP_RECOVER] and attack.spec:
				duration = {State.SWEEP_TELL: attack.spec.startup, State.SWEEP: attack.spec.active, State.SWEEP_RECOVER: attack.spec.recovery}[state]
				progress = 1.0 - attack._phase_left / duration if duration > 0.0 else 1.0
				visual_facing = attack.spec.facing
			_presentation.update(clip, delta, visual_facing, duration, progress)
			return
		art.flip_h = facing < 0
		art.frame = FRAMES.get(state, 0)
		return
	var kneeling: bool = state in [State.SWEEP_RECOVER, State.EXHAUSTED, State.DEAD]
	body.offset_top = -20.0 if kneeling else -56.0
	body.color = Color(0.243, 0.294, 0.369) if state != State.STAGGER else Color(0.6, 0.3, 0.2)
	seal.color = Color(0.94, 0.65, 0.35) if vulnerable else Color(0.137, 0.169, 0.216)
	seal.position.y = 0.0 if kneeling else -30.0
	censer.visible = state in [State.RAIN_TELL, State.RAIN]
	scythe.visible = state in [State.SWEEP_TELL, State.SWEEP, State.SWEEP_RECOVER]
	match state:
		State.SWEEP_TELL:
			scythe.size = Vector2(6, 70)
			scythe.position = Vector2(-facing * 26.0 - 3.0, -100.0)
		State.SWEEP:
			scythe.size = Vector2(sweep_reach, 10)
			scythe.position = Vector2(0.0 if facing > 0 else -sweep_reach, 40.0)
		State.SWEEP_RECOVER:
			scythe.size = Vector2(40, 6)
			scythe.position = Vector2(facing * 24.0 if facing > 0 else -64.0, 50.0)
