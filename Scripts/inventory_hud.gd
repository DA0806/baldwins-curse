class_name InventoryHUD
extends CanvasLayer

## Grupo por el que el jugador encuentra el HUD para (re)enlazar su inventario.
const GROUP: StringName = &"inventory_hud"

const SWAP_SLOT_TINT := Color(1, 1, 1)
const OTHER_SLOT_TINT := Color(0.5, 0.5, 0.5)

# Referencias a los TextureRect donde se dibujarán los iconos
@onready var weapon_icon_0: TextureRect = $MarginContainer/HBoxContainer/WeaponSlot0/WeaponIcon0
@onready var weapon_icon_1: TextureRect = $MarginContainer/HBoxContainer/WeaponSlot1/WeaponIcon1
@onready var mask_icon: TextureRect = $MarginContainer/HBoxContainer/MaskSlot/MaskIcon
@onready var weapon_panels: Array[PanelContainer] = [
	$MarginContainer/HBoxContainer/WeaponSlot0,
	$MarginContainer/HBoxContainer/WeaponSlot1,
]
@onready var weapon_key_labels: Array[Label] = [
	$MarginContainer/HBoxContainer/WeaponSlot0/KeyLabel,
	$MarginContainer/HBoxContainer/WeaponSlot1/KeyLabel,
]
@onready var mask_key_label: Label = $MarginContainer/HBoxContainer/MaskSlot/KeyLabel
@onready var health_bar: ProgressBar = $HealthBar
@onready var mask_name_label: Label = $MarginContainer/HBoxContainer/MaskInfo/MaskName
@onready var mask_effect_label: Label = $MarginContainer/HBoxContainer/MaskInfo/MaskEffect
@onready var mask_cooldown_bar: ProgressBar = $MarginContainer/HBoxContainer/MaskInfo/MaskCooldown

var inventory_ref: PlayerInventory = null
var health_ref: Health = null

func _ready() -> void:
	add_to_group(GROUP)
	_update_swap_slot()
	# Busca el inventario del jugador automáticamente en la escena actual.
	# Si el jugador aparece después, él mismo llama a setup_inventory por el grupo.
	var player = get_tree().get_first_node_in_group("player")
	if player:
		var inv: PlayerInventory = player.get_node_or_null("PlayerInventory") as PlayerInventory
		if not inv and "inventory" in player:
			inv = player.get("inventory") as PlayerInventory
		if inv:
			setup_inventory(inv)
		var player_health := player.get_node_or_null("Health") as Health
		if player_health:
			setup_health(player_health)

## Enlaza la barra de salud. Idempotente, igual que setup_inventory.
func setup_health(health: Health) -> void:
	if health != health_ref:
		if is_instance_valid(health_ref) and health_ref.health_changed.is_connected(_on_health_changed):
			health_ref.health_changed.disconnect(_on_health_changed)
		health_ref = health
		if is_instance_valid(health_ref):
			health_ref.health_changed.connect(_on_health_changed)
	if is_instance_valid(health_ref):
		_on_health_changed(health_ref.current, health_ref.max_health)

func _on_health_changed(current: float, maximum: float) -> void:
	health_bar.max_value = maximum
	health_bar.value = current

## Conecta las señales del PlayerInventory con la UI. Es idempotente: llamarla
## otra vez con el mismo inventario sólo refresca, y con uno nuevo desconecta
## el anterior antes de enlazar.
func setup_inventory(inventory: PlayerInventory) -> void:
	if inventory != inventory_ref:
		_set_connected(inventory_ref, false)
		inventory_ref = inventory
		_set_connected(inventory_ref, true)
	_update_all_slots()

func _set_connected(inventory: PlayerInventory, connected: bool) -> void:
	if not is_instance_valid(inventory):
		return
	var links: Dictionary = {
		inventory.weapon_swapped: _on_weapon_swapped,
		inventory.mask_changed: _on_mask_changed,
		inventory.mask_list_updated: _on_mask_list_updated,
		inventory.swap_slot_changed: _on_swap_slot_changed,
	}
	for sig: Signal in links:
		var callback: Callable = links[sig]
		if connected and not sig.is_connected(callback):
			sig.connect(callback)
		elif not connected and sig.is_connected(callback):
			sig.disconnect(callback)

func _update_all_slots() -> void:
	var has_inventory: bool = is_instance_valid(inventory_ref)
	_update_slot_icon(weapon_icon_0, inventory_ref.get_weapon(0) if has_inventory else null)
	_update_slot_icon(weapon_icon_1, inventory_ref.get_weapon(1) if has_inventory else null)
	_update_mask()
	_update_swap_slot()

## Recarga del cambio de máscara: barra que se vacía e icono apagado.
func _process(_delta: float) -> void:
	var ratio: float = inventory_ref.get_mask_cooldown_ratio() if is_instance_valid(inventory_ref) else 0.0
	mask_cooldown_bar.value = ratio * 100.0
	mask_cooldown_bar.visible = ratio > 0.0
	mask_icon.modulate = Color(0.45, 0.45, 0.45) if ratio > 0.0 else Color.WHITE

## Icono (la forma distingue cada máscara), nombre y efecto de la activa.
func _update_mask() -> void:
	var mask: MaskData = inventory_ref.get_active_mask() if is_instance_valid(inventory_ref) else null
	_update_slot_icon(mask_icon, mask)
	mask_name_label.text = mask.name if mask else "Sin máscara"
	mask_effect_label.text = mask.description if mask else ""

## Marca la ranura de intercambio (borde encendido y tecla entre corchetes)
## y toma las teclas del InputMap.
func _update_swap_slot() -> void:
	var swap_slot: int = inventory_ref.active_weapon_slot if is_instance_valid(inventory_ref) else 0
	var attack_actions: Array[StringName] = [&"attack_weapon_1", &"attack_weapon_2"]
	for i in weapon_panels.size():
		var is_swap: bool = i == swap_slot
		var key: String = InputHints.key_text(attack_actions[i])
		weapon_panels[i].self_modulate = SWAP_SLOT_TINT if is_swap else OTHER_SLOT_TINT
		weapon_key_labels[i].text = "[%s]" % key if is_swap else key
	mask_key_label.text = "%s/%s" % [InputHints.key_text(&"prev_mask"), InputHints.key_text(&"next_mask")]

func _on_weapon_swapped(slot: int, new_weapon: WeaponData, _old_weapon: WeaponData) -> void:
	if slot == 0:
		_update_slot_icon(weapon_icon_0, new_weapon)
	elif slot == 1:
		_update_slot_icon(weapon_icon_1, new_weapon)

func _on_mask_changed(_new_mask: MaskData, _old_mask: MaskData) -> void:
	_update_mask()

func _on_mask_list_updated() -> void:
	_update_mask()

func _on_swap_slot_changed(_slot: int) -> void:
	_update_swap_slot()

func _update_slot_icon(target_rect: TextureRect, item: ItemData) -> void:
	if not target_rect:
		return
	if item and item.icon:
		target_rect.texture = item.icon
		target_rect.visible = true
	else:
		target_rect.texture = null
		target_rect.visible = false
