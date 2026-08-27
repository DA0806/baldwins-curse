class_name InventoryHUD
extends CanvasLayer

# Referencias a los TextureRect donde se dibujarán los iconos
@onready var weapon_icon_0: TextureRect = $MarginContainer/HBoxContainer/WeaponSlot0/WeaponIcon0
@onready var weapon_icon_1: TextureRect = $MarginContainer/HBoxContainer/WeaponSlot1/WeaponIcon1
@onready var mask_icon: TextureRect = $MarginContainer/HBoxContainer/MaskSlot/MaskIcon

var inventory_ref: PlayerInventory = null

func _ready() -> void:
	# Busca el inventario del jugador automáticamente en la escena actual
	var player = get_tree().get_first_node_in_group("player")
	if player:
		var inv: PlayerInventory = player.get_node_or_null("PlayerInventory") as PlayerInventory
		if not inv and "inventory" in player:
			inv = player.get("inventory") as PlayerInventory
		if inv:
			setup_inventory(inv)

## Conecta las señales del PlayerInventory con la UI
func setup_inventory(inventory: PlayerInventory) -> void:
	inventory_ref = inventory
	
	# Conectar señales para actualización en tiempo real
	inventory.weapon_swapped.connect(_on_weapon_swapped)
	inventory.mask_changed.connect(_on_mask_changed)
	
	# Cargar los datos iniciales que ya tenga equipados
	_update_all_slots()

func _update_all_slots() -> void:
	if not inventory_ref:
		return
		
	# Actualizar arma 1
	_update_slot_icon(weapon_icon_0, inventory_ref.weapons[0])
	# Actualizar arma 2
	_update_slot_icon(weapon_icon_1, inventory_ref.weapons[1])
	# Actualizar máscara activa
	_update_slot_icon(mask_icon, inventory_ref.get_active_mask())

func _on_weapon_swapped(slot: int, new_weapon: WeaponData, _old_weapon: WeaponData) -> void:
	if slot == 0:
		_update_slot_icon(weapon_icon_0, new_weapon)
	elif slot == 1:
		_update_slot_icon(weapon_icon_1, new_weapon)

func _on_mask_changed(new_mask: MaskData, _old_mask: MaskData) -> void:
	_update_slot_icon(mask_icon, new_mask)

func _update_slot_icon(target_rect: TextureRect, item: ItemData) -> void:
	if not target_rect:
		return
	if item and item.icon:
		target_rect.texture = item.icon
		target_rect.visible = true
	else:
		target_rect.texture = null
		target_rect.visible = false
