class_name PlayerInventory
extends Node

# Señales para conectar con la UI o el Player Controller
signal weapon_swapped(slot_index: int, new_weapon: WeaponData, old_weapon: WeaponData)
signal mask_changed(new_mask: MaskData, previous_mask: MaskData)
signal mask_list_updated()

# Slots fijos para 2 armas (Dead Cells style)
@export var weapons: Array[WeaponData] = [null, null]

# Colección de máscaras equipadas (Lista Circular)
@export var max_carried_masks: int = 3
var carried_masks: Array[MaskData] = []
var active_mask_index: int = 0
var mask_swap_timer: float = 0.0

func _process(delta: float) -> void:
	if mask_swap_timer > 0.0:
		mask_swap_timer -= delta

# ==========================================
# LÓGICA DE ARMAS
# ==========================================

## Equipa o intercambia un arma en el slot especificado (0 o 1). Devuelve el arma que se desequipa.
func equip_weapon(slot: int, new_weapon: WeaponData) -> WeaponData:
	if slot < 0 or slot > 1:
		return null
		
	var old_weapon: WeaponData = weapons[slot]
	weapons[slot] = new_weapon
	
	weapon_swapped.emit(slot, new_weapon, old_weapon)
	return old_weapon

# ==========================================
# LÓGICA DE MÁSCARAS (CICLADO EN COMBATE & SWAP)
# ==========================================

## Cicla entre las máscaras que lleva el jugador (1: siguiente, -1: anterior)
func cycle_mask(direction: int = 1) -> MaskData:
	if carried_masks.is_empty() or mask_swap_timer > 0.0:
		return get_active_mask()
		
	var prev_mask: MaskData = get_active_mask()
	
	# Comportamiento de buffer circular: (index + dir) mod len
	active_mask_index = (active_mask_index + direction) % carried_masks.size()
	if active_mask_index < 0:
		active_mask_index = carried_masks.size() - 1
		
	var new_mask: MaskData = carried_masks[active_mask_index]
	mask_swap_timer = new_mask.swap_cooldown
	
	mask_changed.emit(new_mask, prev_mask)
	return new_mask

## Añade una máscara al cinto o reemplaza la activa si está lleno el límite
func add_or_swap_mask(new_mask: MaskData) -> MaskData:
	var dropped_mask: MaskData = null
	
	if carried_masks.size() < max_carried_masks:
		carried_masks.append(new_mask)
		# Si es la primera, queda activa
		if carried_masks.size() == 1:
			active_mask_index = 0
			mask_changed.emit(new_mask, null)
	else:
		# Intercambia con la máscara actualmente activa
		dropped_mask = carried_masks[active_mask_index]
		carried_masks[active_mask_index] = new_mask
		mask_changed.emit(new_mask, dropped_mask)
		
	mask_list_updated.emit()
	return dropped_mask

func get_active_mask() -> MaskData:
	if carried_masks.is_empty():
		return null
	return carried_masks[active_mask_index]
