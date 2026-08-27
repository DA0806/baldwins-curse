class_name PlayerInventory
extends Node

signal weapon_swapped(slot_index: int, new_weapon: WeaponData, old_weapon: WeaponData)
signal mask_changed(new_mask: MaskData, previous_mask: MaskData)
signal mask_list_updated()

# Referencia a la escena para instanciar objetos en el suelo al soltar
const ITEM_PICKUP_SCENE: PackedScene = preload("res://Scenes/Items/ItemPickup.tscn")

@export var weapons: Array[WeaponData] = [null, null]
@export var active_weapon_slot: int = 0 # 0 = Arma Principal, 1 = Arma Secundaria

@export var max_carried_masks: int = 3
var carried_masks: Array[MaskData] = []
var active_mask_index: int = 0
var mask_swap_timer: float = 0.0

func _process(delta: float) -> void:
	if mask_swap_timer > 0.0:
		mask_swap_timer -= delta

# ==========================================
# GESTIÓN INTELIGENTE DE ARMAS
# ==========================================

## Equipa o intercambia un arma en un slot específico
func equip_weapon(slot: int, new_weapon: WeaponData) -> WeaponData:
	if slot < 0 or slot >= weapons.size():
		return null
		
	var old_weapon: WeaponData = weapons[slot]
	weapons[slot] = new_weapon
	
	weapon_swapped.emit(slot, new_weapon, old_weapon)
	return old_weapon

## Equipa un arma: si hay un slot libre lo usa, sino intercambia con el slot activo
func equip_or_swap_weapon(new_weapon: WeaponData) -> WeaponData:
	# 1. Si el slot secundario está vacío y el primario ocupado, equipa en el secundario
	if weapons[0] != null and weapons[1] == null:
		weapons[1] = new_weapon
		weapon_swapped.emit(1, new_weapon, null)
		return null # No soltó nada
		
	# 2. Si ambos están ocupados (o el primario está vacío), reemplaza en el slot activo
	var old_weapon: WeaponData = weapons[active_weapon_slot]
	weapons[active_weapon_slot] = new_weapon
	weapon_swapped.emit(active_weapon_slot, new_weapon, old_weapon)
	
	return old_weapon # Devuelve el arma vieja para que quede en el suelo

## Suelta el arma activa físicamente al suelo (ej. al presionar 'G')
func drop_active_weapon(drop_position: Vector2) -> void:
	var weapon_to_drop: WeaponData = weapons[active_weapon_slot]
	if not weapon_to_drop:
		return
		
	# Instanciar el pickup en el mundo
	var pickup = ITEM_PICKUP_SCENE.instantiate() as ItemPickup
	pickup.item_data = weapon_to_drop
	pickup.global_position = drop_position
	
	# Añadir al mapa actual
	get_tree().current_scene.add_child(pickup)
	
	# Vaciar el slot
	weapons[active_weapon_slot] = null
	weapon_swapped.emit(active_weapon_slot, null, weapon_to_drop)

## Intercambia la posición entre Arma 1 y Arma 2 (ej. con tecla TAB o botón X)
func switch_active_weapon_slot() -> void:
	active_weapon_slot = 1 if active_weapon_slot == 0 else 0

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

## Devuelve la máscara actualmente equipada/activa
func get_active_mask() -> MaskData:
	if carried_masks.is_empty() or active_mask_index >= carried_masks.size():
		return null
	return carried_masks[active_mask_index]
