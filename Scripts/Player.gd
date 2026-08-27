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

# Timers internos
var coyote_timer: float = 0.0
var jump_buffer_timer: float = 0.0

# Referencias a Nodos
@onready var sprite: Sprite2D = $Sprite2D # O AnimatedSprite2D
@onready var ray_left: RayCast2D = $RayLeft
@onready var ray_right: RayCast2D = $RayRight

func _physics_process(delta: float) -> void:
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
	if velocity.x > 5:
		sprite.flip_h = false
	elif velocity.x < -5:
		sprite.flip_h = true
		
@onready var inventory: PlayerInventory = $PlayerInventory

# --------------------------------------
# --------- Lógica de combate ----------
#---------------------------------------

func _unhandled_input(event: InputEvent) -> void:
	if Input.is_action_just_pressed("next_mask"):
		inventory.cycle_mask(1)
	elif Input.is_action_just_pressed("prev_mask"):
		inventory.cycle_mask(-1)

	if Input.is_action_just_pressed("attack_weapon_1"):
		execute_attack(inventory.weapons[0])
	elif Input.is_action_just_pressed("attack_weapon_2"):
		execute_attack(inventory.weapons[1])

func execute_attack(weapon: WeaponData) -> void:
	if not weapon:
		return
	var active_mask: MaskData = inventory.get_active_mask()
	# Aquí aplicas el daño base del arma modificado por la máscara activa
	print("Atacando con: ", weapon.name, " | Máscara activa: ", active_mask.name if active_mask else "Ninguna")
