class_name ItemPickup
extends Area2D

@export var item_data: ItemData:
	set(value):
		item_data = value
		update_appearance()

# Si quieres que solo diga el nombre ("Espada") o con tecla ("[E] Espada")
@export var show_key_prompt: bool = true

# ==============================================================
#  VISUALES — brillo que barre el ítem (shader de shine)
# ==============================================================
@export_group("Brillo")

## Color del destello. El canal alfa controla la intensidad.
@export var shine_color: Color = Color(1.0, 1.0, 1.0, 0.6)

## Duración de cada barrido (el "SHINE_TIME" del ejemplo original).
@export_range(0.1, 3.0, 0.05) var shine_duration: float = 0.8

## Pausa entre barrido y barrido.
@export_range(0.0, 5.0, 0.1) var shine_pause: float = 1.6

## Ángulo del brillo en grados.
@export_range(0.0, 89.9, 0.1) var shine_angle: float = 45.0

# Ancho del brillo al inicio/fin de cada barrido (valores del ejemplo original)
const SHINE_SIZE_MAX := 0.13
const SHINE_SIZE_MIN := 0.01

var _shine_tween: Tween

@onready var sprite: Sprite2D = $Sprite2D
@onready var prompt_label: Label = $Label

var player_in_range: PlayerInventory = null

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	
	# Centrar el Label automáticamente si no lo está
	if prompt_label:
		prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		prompt_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	
	update_appearance()
	_setup_shine()

# ==============================================================
#  VISUALES — implementación
# ==============================================================
func _setup_shine() -> void:
	if not sprite.material is ShaderMaterial:
		push_warning("ItemPickup (%s): el Sprite2D necesita un ShaderMaterial con el shader de brillo." % name)
		return
	
	# Duplicamos el material para que cada pickup anime el suyo propio.
	# Si no, todos los ítems del mapa compartirían el mismo material
	# y sus brillos se pisarían entre sí.
	var mat := sprite.material.duplicate() as ShaderMaterial
	sprite.material = mat
	
	# Valores iniciales (equivalen a los "from" del ejemplo original)
	mat.set_shader_parameter("shine_color", shine_color)
	mat.set_shader_parameter("shine_angle", shine_angle)
	mat.set_shader_parameter("shine_size", SHINE_SIZE_MAX)
	mat.set_shader_parameter("shine_progress", 1.0)
	
	_start_shine_loop(mat)


func _start_shine_loop(mat: ShaderMaterial) -> void:
	_shine_tween = create_tween()
	_shine_tween.set_loops()
	
	# --- Barrido de ida: el brillo cruza el ítem (progreso 1.0 → 0.0) ---
	_shine_tween.set_parallel(true)
	_shine_tween.tween_property(mat, "shader_parameter/shine_progress", 0.0, shine_duration) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	# El brillo se adelgaza (arranca al 25% del barrido)
	_shine_tween.tween_property(mat, "shader_parameter/shine_size", SHINE_SIZE_MIN, shine_duration * 0.75) \
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN) \
		.set_delay(shine_duration * 0.25)
	
	# --- Barrido de vuelta: el brillo regresa (progreso 0.0 → 1.0) ---
	_shine_tween.set_parallel(false)
	_shine_tween.tween_property(mat, "shader_parameter/shine_progress", 1.0, 0)
	# El brillo vuelve a engordar
	_shine_tween.parallel().tween_property(mat, "shader_parameter/shine_size", SHINE_SIZE_MAX, 0) \
		\
		.set_delay(shine_duration * 0.25)
	
	# --- Pausa antes de repetir ---
	_shine_tween.tween_interval(shine_pause)

# ==============================================================
#  (Todo tu código original sin cambios desde aquí)
# ==============================================================

func update_appearance() -> void:
	if not is_inside_tree() or not prompt_label or not sprite:
		return
		
	if item_data:
		sprite.texture = item_data.icon
		if show_key_prompt:
			prompt_label.text = "[R] " + item_data.name
		else:
			prompt_label.text = item_data.name
	else:
		sprite.texture = null
		prompt_label.text = ""
	
	prompt_label.visible = false

func _unhandled_input(event: InputEvent) -> void:
	if player_in_range and event.is_action_pressed("interact") and not event.is_echo():
		pick_up()

func pick_up() -> void:
	if not item_data or not player_in_range:
		return
		
	var dropped_item: ItemData = null
	
	if item_data is WeaponData:
		dropped_item = player_in_range.equip_or_swap_weapon(item_data as WeaponData)
	elif item_data is MaskData:
		dropped_item = player_in_range.add_or_swap_mask(item_data as MaskData)
		
	if dropped_item:
		item_data = dropped_item
		update_appearance()
	else:
		queue_free()

func _get_player_inventory(body: Node) -> PlayerInventory:
	if not body:
		return null
	var inv: PlayerInventory = body.get_node_or_null("PlayerInventory") as PlayerInventory
	if not inv and "inventory" in body:
		inv = body.get("inventory") as PlayerInventory
	return inv

func _on_body_entered(body: Node2D) -> void:
	var inv: PlayerInventory = _get_player_inventory(body)
	if inv:
		player_in_range = inv
		if prompt_label and item_data:
			prompt_label.visible = true

func _on_body_exited(body: Node2D) -> void:
	if player_in_range and _get_player_inventory(body) == player_in_range:
		player_in_range = null
		if prompt_label:
			prompt_label.visible = false
