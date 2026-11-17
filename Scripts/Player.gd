extends CharacterBody2D

# ==========================================
# PARÁMETROS CONFIGURABLES (Game Feel)
# ==========================================
@export_group("Movimiento Horizontal")
@export var max_speed: float = 180.0
@export var acceleration: float = 1200.0
@export var friction: float = 1500.0
@export var air_control_multiplier: float = 0.7

@export_group("Físicas de Salto")
@export var jump_velocity: float = -380.0
@export var min_jump_velocity: float = -150.0
@export var base_gravity: float = 980.0
@export var fall_gravity_multiplier: float = 1.6 # Caída más rápida para peso "Soulslike"
@export var max_fall_speed: float = 650.0

@export_group("Asistencias de Jugabilidad (Alva Majo)")
@export var coyote_time_max: float = 0.12 # Segundos de gracia tras caer
@export var jump_buffer_max: float = 0.14 # Segundos para registrar salto antes de tocar suelo
@export var corner_correction_distance: float = 3.0 # Píxeles que se ajusta el personaje

# Máquina de estados
enum State {
	IDLE,
	WALK,
	JUMP,
	ATTACK,
	DEAD,
}
var current_state: State = State.IDLE

# Timers internos
var coyote_timer: float = 0.0
var jump_buffer_timer: float = 0.0

# Referencias a Nodos
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var ray_left: RayCast2D = $RayLeft
@onready var ray_right: RayCast2D = $RayRight
@onready var inventory: PlayerInventory = $PlayerInventory
@onready var camera: Camera2D = $Camera2D
@onready var health: Health = $Health
@onready var hurtbox: Hurtbox = $Hurtbox
@onready var attack: MeleeAttack = $MeleeAttack

@export_group("Combate")
## Empuje al recibir daño: x se aleja del atacante, y es hacia arriba.
@export var hurt_knockback: Vector2 = Vector2(160.0, -140.0)

# Duración de los cuadros de preparación de la animación Attack (todos menos el último).
var _attack_windup_length: float = 0.0

# Desplazamiento horizontal del sprite respecto al pivote (pies), tomado de la escena.
var _sprite_pivot_x: float = 0.0

func _ready() -> void:
	_sprite_pivot_x = absf(sprite.offset.x)
	var frames := sprite.sprite_frames
	_attack_windup_length = (frames.get_frame_count(&"Attack") - 1) / frames.get_animation_speed(&"Attack")
	attack.finished.connect(_on_attack_finished)
	attack.phase_changed.connect(_on_attack_phase_changed)
	attack.hit_landed.connect(func(_target: Hurtbox, _damage: float): SoundBank.play(self, &"hit"))
	health.damage_modifier = inventory.modify_incoming_damage
	health.damaged.connect(_on_damaged)
	health.died.connect(_on_died)
	sprite.play("Idle")
	# Enlaza (o reenlaza) cualquier HUD presente con este inventario y esta salud.
	get_tree().call_group(InventoryHUD.GROUP, "setup_inventory", inventory)
	get_tree().call_group(InventoryHUD.GROUP, "setup_health", health)

## Devuelve al jugador a la vida con la salud completa (reintento).
func revive() -> void:
	health.reset()
	sprite.modulate = Color.WHITE
	sprite.speed_scale = 1.0
	current_state = State.JUMP # fuerza el cambio de animación
	change_state(State.IDLE)

## Recoloca al jugador (caída, reintento) sin arrastrar velocidad, timers ni cámara.
func respawn_at(spawn_position: Vector2) -> void:
	attack.cancel()
	global_position = spawn_position
	velocity = Vector2.ZERO
	coyote_timer = 0.0
	jump_buffer_timer = 0.0
	if current_state != State.DEAD:
		current_state = State.JUMP # fuerza el cambio de animación
		change_state(State.IDLE)
	if camera and camera.has_method("snap_to_target"):
		camera.snap_to_target()

func _physics_process(delta: float) -> void:
	# 0. Muerto: sólo cae y se detiene, sin leer entradas.
	if current_state == State.DEAD:
		apply_gravity(delta)
		velocity.x = move_toward(velocity.x, 0.0, friction * delta)
		move_and_slide()
		return
	
	# 1. Actualizar timers
	update_timers(delta)
	
	# 2. Manejo de Gravedad
	apply_gravity(delta)
	
	# 3. Buffer de entrada para el salto
	if Input.is_action_just_pressed("jump"):
		jump_buffer_timer = jump_buffer_max
	
	# 4. Comprobación y ejecución del Salto
	handle_jump()
	
	# 5. Salto de altura variable (Cortar salto al soltar botón)
	handle_variable_jump()
	
	# 6. Movimiento horizontal y fricción
	handle_horizontal_movement(delta)
	
	# 7. Corrección de esquinas al subir
	handle_corner_correction()
	
	# 8. Mover y deslizar
	move_and_slide()
	
	# 9. Orientar el Sprite según la dirección
	update_sprite_direction()
	
	# 10. Actualizar máquina de estados y animaciones
	update_animation_state()

# ==========================================
# LÓGICA DE JUGABILIDAD
# ==========================================

func update_timers(delta: float) -> void:
	# Coyote Time: Si está en el suelo, recargamos el timer; si cae, empieza a agotarse
	if is_on_floor():
		coyote_timer = coyote_time_max
	else:
		coyote_timer = max(0.0, coyote_timer - delta)
	
	# Jump Buffer Timer
	if jump_buffer_timer > 0.0:
		jump_buffer_timer = max(0.0, jump_buffer_timer - delta)

func apply_gravity(delta: float) -> void:
	if not is_on_floor():
		# Si está cayendo o subiendo pero ya no presiona el salto, la gravedad es mayor
		var current_gravity = base_gravity
		if velocity.y > 0:
			current_gravity *= fall_gravity_multiplier
		
		velocity.y += current_gravity * delta
		velocity.y = min(velocity.y, max_fall_speed)

func handle_jump() -> void:
	# Puede saltar si presionó saltar recientemente Y tiene coyote time disponible
	if jump_buffer_timer > 0.0 and coyote_timer > 0.0:
		velocity.y = jump_velocity
		jump_buffer_timer = 0.0
		coyote_timer = 0.0

func handle_variable_jump() -> void:
	# Si soltamos la tecla mientras aún vamos hacia arriba a gran velocidad, truncamos el salto
	if Input.is_action_just_released("jump") and velocity.y < min_jump_velocity:
		velocity.y = min_jump_velocity

func handle_horizontal_movement(delta: float) -> void:
	var direction := Input.get_axis("move_left", "move_right")
	var accel = acceleration
	var frict = friction
	
	# Menor control en el aire para dar sensación de inercia
	if not is_on_floor():
		accel *= air_control_multiplier
		frict *= air_control_multiplier
	
	if direction != 0:
		velocity.x = move_toward(velocity.x, direction * max_speed, accel * delta)
	else:
		velocity.x = move_toward(velocity.x, 0.0, frict * delta)

func handle_corner_correction() -> void:
	# Si el personaje va subiendo y solo uno de los rayos choca con el borde de un bloque
	if velocity.y < 0:
		if ray_left.is_colliding() and not ray_right.is_colliding():
			position.x += corner_correction_distance
		elif ray_right.is_colliding() and not ray_left.is_colliding():
			position.x -= corner_correction_distance

func update_sprite_direction() -> void:
	# La orientación queda fijada mientras dura un ataque.
	if attack.phase != MeleeAttack.Phase.IDLE:
		return
	# Sigue a la dirección pulsada, no a la velocidad: el empuje al recibir
	# daño no debe dejar al jugador de espaldas.
	var direction := Input.get_axis("move_left", "move_right")
	if direction > 0.0:
		sprite.flip_h = false
	elif direction < 0.0:
		sprite.flip_h = true
	# flip_h voltea la textura dentro de su rectángulo; el offset se invierte
	# para que el pivote (pies) quede en el mismo punto en ambas direcciones.
	sprite.offset.x = -_sprite_pivot_x if sprite.flip_h else _sprite_pivot_x

func update_animation_state() -> void:
	# Si está atacando, se deja correr la animación hasta que termine
	if current_state == State.ATTACK or current_state == State.DEAD:
		return
	
	if not is_on_floor():
		change_state(State.JUMP)
	elif abs(velocity.x) > 5.0:
		change_state(State.WALK)
	else:
		change_state(State.IDLE)

func change_state(new_state: State) -> void:
	# Permitir reiniciar animación si es ataque o si cambia de estado
	if current_state == new_state and new_state != State.ATTACK:
		return
	
	current_state = new_state
	match current_state:
		State.IDLE:
			sprite.play("Idle")
		State.WALK:
			sprite.play("Walk")
		State.JUMP:
			sprite.play("Jump")
		State.ATTACK:
			sprite.play("Attack")
		State.DEAD:
			sprite.play("Dead")

func _on_attack_phase_changed(phase: int) -> void:
	# La ventana activa siempre coincide con el cuadro del tajo (el último).
	if phase == MeleeAttack.Phase.ACTIVE and current_state == State.ATTACK:
		sprite.frame = sprite.sprite_frames.get_frame_count(&"Attack") - 1

func _on_attack_finished(_interrupted: bool) -> void:
	# Al terminar (o interrumpirse) el ataque, regresar al estado que corresponda
	sprite.speed_scale = 1.0
	if current_state == State.ATTACK:
		if not is_on_floor():
			change_state(State.JUMP)
		elif abs(velocity.x) > 5.0:
			change_state(State.WALK)
		else:
			change_state(State.IDLE)

# --------------------------------------
# --------- Lógica de combate ----------
#---------------------------------------

func _unhandled_input(event: InputEvent) -> void:
	if current_state == State.DEAD or event.is_echo():
		return
	# El jugador es el único dueño de la entrada de interacción.
	if event.is_action_pressed("interact") and not event.is_echo():
		if try_interact() != PlayerInventory.PickupStatus.REJECTED:
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("next_mask") or event.is_action_pressed("prev_mask"):
		var before: MaskData = inventory.get_active_mask()
		inventory.cycle_mask(1 if event.is_action_pressed("next_mask") else -1)
		if inventory.get_active_mask() != before:
			SoundBank.play(self, &"mask")
	elif event.is_action_pressed("attack_weapon_1"):
		execute_attack(0)
	elif event.is_action_pressed("attack_weapon_2"):
		execute_attack(1)

# --------------------------------------
# ------------ Interacción -------------
#---------------------------------------

## Pickup elegible más cercano. Empate estable: gana el primero en orden de
## árbol de escena (el orden en que get_nodes_in_group devuelve los nodos).
func find_interact_target() -> ItemPickup:
	var best: ItemPickup = null
	var best_distance: float = INF
	for node in get_tree().get_nodes_in_group(ItemPickup.GROUP):
		var pickup := node as ItemPickup
		if not pickup or not pickup.can_be_picked_by(inventory):
			continue
		var distance: float = global_position.distance_squared_to(pickup.global_position)
		if distance < best_distance:
			best = pickup
			best_distance = distance
	return best

## Una pulsación = una transacción con un solo pickup.
func try_interact() -> int:
	var target := find_interact_target()
	if not target:
		return PlayerInventory.PickupStatus.REJECTED
	var status: int = target.pick_up()
	if status != PlayerInventory.PickupStatus.REJECTED:
		SoundBank.play(self, &"pickup")
	return status

## Pide un ataque con el arma de una ranura. Devuelve true si se aceptó.
## Una ranura vacía, un ataque en curso o el enfriamiento lo rechazan sin
## animación ni daño. Los datos del golpe se fijan aquí, al aceptarlo.
func execute_attack(slot: int) -> bool:
	var weapon: WeaponData = inventory.get_weapon(slot)
	if not weapon or current_state == State.DEAD:
		return false
	
	var spec := MeleeAttack.Spec.new()
	# Máscara ofensiva: se captura aquí, al aceptar el ataque. Cambiar de
	# máscara durante el ataque no altera este valor.
	spec.damage = inventory.modify_weapon_damage(weapon.base_damage)
	spec.reach = weapon.reach
	spec.height = weapon.hit_height
	spec.startup = weapon.startup
	spec.active = weapon.active_time
	spec.recovery = weapon.recovery
	spec.cooldown = weapon.attack_cooldown
	spec.facing = -1 if sprite.flip_h else 1
	if not attack.start(spec):
		return false
	
	# El último ataque válido decide qué ranura recibirá un intercambio.
	inventory.active_weapon_slot = slot
	SoundBank.play(self, &"attack")
	# Los cuadros de preparación duran lo que la anticipación; el último cuadro
	# (el tajo) aparece al abrirse la ventana activa y se mantiene en la recuperación.
	sprite.speed_scale = _attack_windup_length / maxf(spec.startup, 0.01)
	change_state(State.ATTACK)
	return true

func _on_damaged(_amount: float, source: Node) -> void:
	attack.cancel()
	SoundBank.play(self, &"hit", 0.7)
	var away: float = 1.0
	if source is Node2D and (source as Node2D).global_position.x > global_position.x:
		away = -1.0
	velocity = Vector2(away * hurt_knockback.x, hurt_knockback.y)
	sprite.modulate = Color(1.0, 0.7, 0.7) if GameSettings.reduced_effects else Color(1.0, 0.4, 0.4)
	create_tween().tween_property(sprite, "modulate", Color.WHITE, maxf(health.invulnerability_time, 0.1))

func _on_died(_source: Node) -> void:
	attack.cancel()
	sprite.speed_scale = 1.0
	current_state = State.DEAD
	sprite.play("Dead")
