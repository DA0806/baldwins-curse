class_name PlayerInventory
extends Node

signal weapon_swapped(slot_index: int, new_weapon: WeaponData, old_weapon: WeaponData)
signal mask_changed(new_mask: MaskData, previous_mask: MaskData)
signal mask_list_updated()
## La ranura que recibirá el intercambio cuando ambas armas estén ocupadas.
signal swap_slot_changed(slot_index: int)

# Referencia a la escena para instanciar objetos en el suelo al soltar
const ITEM_PICKUP_SCENE: PackedScene = preload("res://Scenes/Items/ItemPickup.tscn")

const WEAPON_SLOT_COUNT: int = 2

## Resultado de intentar recoger un objeto del mundo.
enum PickupStatus {
	REJECTED, ## Nada cambió (objeto nulo o de un tipo sin manejador).
	STORED,   ## Entró en un hueco libre; el pickup desaparece.
	SWAPPED,  ## Reemplazó a otro objeto, que queda en el suelo.
}

class PickupOutcome:
	var status: int = PickupStatus.REJECTED
	var dropped: ItemData = null

## Siempre tiene exactamente WEAPON_SLOT_COUNT posiciones (null = hueco vacío).
@export var weapons: Array[WeaponData] = [null, null]:
	set(value):
		weapons = value.duplicate()
		weapons.resize(WEAPON_SLOT_COUNT)

## Ranura de intercambio: 0 = Arma Principal, 1 = Arma Secundaria.
@export var active_weapon_slot: int = 0:
	set(value):
		var clamped: int = clampi(value, 0, WEAPON_SLOT_COUNT - 1)
		if clamped == active_weapon_slot:
			return
		active_weapon_slot = clamped
		swap_slot_changed.emit(active_weapon_slot)

## Capacidad del cinto de máscaras. Nunca baja de 1.
@export var max_carried_masks: int = 3:
	set(value):
		max_carried_masks = maxi(1, value)
var carried_masks: Array[MaskData] = []
var active_mask_index: int = 0
var mask_swap_timer: float = 0.0
## Duración del enfriamiento en curso (para dibujar la recarga en el HUD).
var mask_swap_duration: float = 0.0

func _physics_process(delta: float) -> void:
	if mask_swap_timer > 0.0:
		mask_swap_timer = maxf(0.0, mask_swap_timer - delta)

## 0 = listo para cambiar; 1 = el enfriamiento acaba de empezar.
func get_mask_cooldown_ratio() -> float:
	if mask_swap_timer <= 0.0 or mask_swap_duration <= 0.0:
		return 0.0
	return mask_swap_timer / mask_swap_duration

# ==========================================
# MODIFICADORES DE MÁSCARA (cada uno se usa en un único lugar)
# ==========================================

## Daño que recibe el jugador. Lo aplica Health.take_damage.
func modify_incoming_damage(amount: float) -> float:
	var mask: MaskData = get_active_mask()
	return amount * mask.damage_taken_multiplier() if mask else amount

## Daño de arma de un ataque. Lo captura Player.execute_attack al aceptarlo.
func modify_weapon_damage(amount: float) -> float:
	var mask: MaskData = get_active_mask()
	return amount * mask.weapon_damage_multiplier() if mask else amount

# ==========================================
# ESTADO POR IDs (contrato para puntos de control y guardado)
# ==========================================

## Estado del inventario sólo con datos simples: IDs de ItemCatalog.
func to_state() -> Dictionary:
	_ensure_weapon_slots()
	var weapon_ids: Array[String] = []
	for weapon in weapons:
		weapon_ids.append(weapon.id if weapon else "")
	var mask_ids: Array[String] = []
	for mask in carried_masks:
		mask_ids.append(mask.id)
	return {
		"weapons": weapon_ids,
		"swap_slot": active_weapon_slot,
		"masks": mask_ids,
		"active_mask": active_mask_index,
	}

## Reconstruye el inventario desde to_state(). Los IDs desconocidos se omiten.
func from_state(state: Dictionary) -> void:
	var weapon_ids: Array = state.get("weapons", [])
	for slot in WEAPON_SLOT_COUNT:
		var id: String = weapon_ids[slot] if slot < weapon_ids.size() else ""
		equip_weapon(slot, ItemCatalog.get_item(id) as WeaponData)
	active_weapon_slot = int(state.get("swap_slot", 0))
	var previous: MaskData = get_active_mask()
	carried_masks.clear()
	for id in state.get("masks", []):
		var mask := ItemCatalog.get_item(id) as MaskData
		if mask and carried_masks.size() < max_carried_masks:
			carried_masks.append(mask)
	active_mask_index = clampi(int(state.get("active_mask", 0)), 0, maxi(0, carried_masks.size() - 1))
	mask_swap_timer = 0.0
	mask_changed.emit(get_active_mask(), previous)
	mask_list_updated.emit()

# ==========================================
# GESTIÓN INTELIGENTE DE ARMAS
# ==========================================

## Restaura la invariante si alguien modificó el arreglo en sitio.
func _ensure_weapon_slots() -> void:
	if weapons.size() != WEAPON_SLOT_COUNT:
		weapons.resize(WEAPON_SLOT_COUNT)

## Lectura segura de una ranura: una ranura inválida equivale a vacío.
func get_weapon(slot: int) -> WeaponData:
	_ensure_weapon_slots()
	if slot < 0 or slot >= WEAPON_SLOT_COUNT:
		return null
	return weapons[slot]

## Equipa o intercambia un arma en un slot específico
func equip_weapon(slot: int, new_weapon: WeaponData) -> WeaponData:
	_ensure_weapon_slots()
	if slot < 0 or slot >= WEAPON_SLOT_COUNT:
		return null

	var old_weapon: WeaponData = weapons[slot]
	weapons[slot] = new_weapon

	weapon_swapped.emit(slot, new_weapon, old_weapon)
	return old_weapon

## Equipa un arma: usa el primer hueco libre y, si no hay, intercambia con la
## ranura de intercambio. Devuelve el arma desplazada o null.
func equip_or_swap_weapon(new_weapon: WeaponData) -> WeaponData:
	if not new_weapon:
		return null
	_ensure_weapon_slots()

	var slot: int = weapons.find(null)
	if slot == -1:
		slot = active_weapon_slot
	return equip_weapon(slot, new_weapon)

## Punto único de entrada para recoger un objeto del mundo.
func pick_up_item(item: ItemData) -> PickupOutcome:
	var outcome := PickupOutcome.new()
	if item is WeaponData:
		outcome.dropped = equip_or_swap_weapon(item as WeaponData)
	elif item is MaskData:
		outcome.dropped = add_or_swap_mask(item as MaskData)
	else:
		return outcome
	outcome.status = PickupStatus.SWAPPED if outcome.dropped else PickupStatus.STORED
	return outcome

## Suelta el arma activa físicamente al suelo (ej. al presionar 'G')
func drop_active_weapon(drop_position: Vector2) -> void:
	var weapon_to_drop: WeaponData = get_weapon(active_weapon_slot)
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

## Cicla entre las máscaras que lleva el jugador (1: siguiente, -1: anterior).
## Durante el enfriamiento la petición se ignora. Con 0 o 1 máscaras no hay
## cambio efectivo y el enfriamiento no se consume.
func cycle_mask(direction: int = 1) -> MaskData:
	if carried_masks.size() <= 1 or mask_swap_timer > 0.0 or direction == 0:
		return get_active_mask()

	var prev_mask: MaskData = get_active_mask()

	# Buffer circular en ambos sentidos.
	active_mask_index = posmod(active_mask_index + signi(direction), carried_masks.size())

	var new_mask: MaskData = carried_masks[active_mask_index]
	mask_swap_timer = new_mask.swap_cooldown
	mask_swap_duration = new_mask.swap_cooldown

	mask_changed.emit(new_mask, prev_mask)
	return new_mask

## Añade una máscara al cinto o reemplaza la activa si está lleno el límite
func add_or_swap_mask(new_mask: MaskData) -> MaskData:
	if not new_mask:
		return null
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
