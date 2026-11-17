class_name MeleeAttack
extends Node2D

## Un golpe cuerpo a cuerpo con anticipación, ventana activa y recuperación.
## Quien ataca sólo pide `start(spec)`; este nodo decide si se acepta, abre y
## cierra la zona de golpe y avisa del resultado. Los datos del golpe quedan
## fijados en `spec` al aceptarlo.

signal phase_changed(phase: int)
signal hit_landed(target: Hurtbox, damage: float)
## `interrupted` es true si el ataque se canceló antes de terminar.
signal finished(interrupted: bool)

enum Phase { IDLE, STARTUP, ACTIVE, RECOVERY }

class Spec:
	var damage: float = 0.0
	var near: float = 6.0   ## inicio de la zona, en px desde el origen del atacante
	var reach: float = 40.0 ## fin de la zona
	var height: float = 40.0
	var startup: float = 0.1
	var active: float = 0.1
	var recovery: float = 0.2
	var cooldown: float = 0.0 ## desde el inicio del ataque hasta poder iniciar otro
	var facing: int = 1

	func total() -> float:
		return startup + active + recovery

var phase: int = Phase.IDLE
var spec: Spec = null
var cooldown_left: float = 0.0
var _phase_left: float = 0.0

@onready var hitbox: Hitbox = $Hitbox

func _ready() -> void:
	hitbox.hit_landed.connect(func(target: Hurtbox, damage: float): hit_landed.emit(target, damage))

func can_start() -> bool:
	return phase == Phase.IDLE and cooldown_left <= 0.0

## Devuelve false si el ataque se rechaza (otro en curso o enfriamiento).
func start(new_spec: Spec) -> bool:
	if not can_start():
		return false
	spec = new_spec
	cooldown_left = spec.cooldown
	_enter(Phase.STARTUP, spec.startup)
	return true

## Interrumpe el ataque y cierra la zona de golpe (daño recibido, muerte,
## reaparición). El enfriamiento sigue corriendo.
func cancel() -> void:
	if phase == Phase.IDLE:
		return
	hitbox.close()
	phase = Phase.IDLE
	phase_changed.emit(phase)
	finished.emit(true)

func _physics_process(delta: float) -> void:
	if cooldown_left > 0.0:
		cooldown_left = maxf(0.0, cooldown_left - delta)
	if phase == Phase.IDLE:
		return
	_phase_left -= delta
	if _phase_left > 0.0001:
		return
	match phase:
		Phase.STARTUP:
			hitbox.open(spec.damage, spec.near, spec.reach, spec.height, spec.facing)
			_enter(Phase.ACTIVE, spec.active)
		Phase.ACTIVE:
			hitbox.close()
			_enter(Phase.RECOVERY, spec.recovery)
		Phase.RECOVERY:
			phase = Phase.IDLE
			phase_changed.emit(phase)
			finished.emit(false)

func _enter(new_phase: int, duration: float) -> void:
	phase = new_phase
	_phase_left = duration
	phase_changed.emit(phase)

func _exit_tree() -> void:
	# Al salir de la sala no puede quedar una zona de golpe abierta.
	hitbox.close()
	phase = Phase.IDLE
