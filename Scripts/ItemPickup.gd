class_name ItemPickup
extends Area2D

@export var item_data: ItemData:
	set(value):
		item_data = value
		update_appearance()

# Si quieres que solo diga el nombre ("Espada") o con tecla ("[E] Espada")
@export var show_key_prompt: bool = true 

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
	
	# Empieza oculto hasta que el jugador se acerque
	prompt_label.visible = false

func _unhandled_input(event: InputEvent) -> void:
	# Recoger con la tecla E (acción "interact")
	if player_in_range and event.is_action_pressed("interact") and not event.is_echo():
		pick_up()

func pick_up() -> void:
	if not item_data or not player_in_range:
		return
		
	var dropped_item: ItemData = null
	
	if item_data is WeaponData:
		dropped_item = player_in_range.equip_weapon(0, item_data as WeaponData)
	elif item_data is MaskData:
		dropped_item = player_in_range.add_or_swap_mask(item_data as MaskData)
		
	if dropped_item:
		# Si expulsó un item del inventario, lo dejamos en el suelo
		item_data = dropped_item
		update_appearance()
	else:
		# Si había espacio libre, el pickup desaparece del mapa
		queue_free()

func _get_player_inventory(body: Node2D) -> PlayerInventory:
	var inv: PlayerInventory = body.get_node_or_null("PlayerInventory")
	if not inv and "inventory" in body:
		inv = body.inventory as PlayerInventory
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
