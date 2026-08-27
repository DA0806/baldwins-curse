class_name MaskData
extends ItemData

@export var passive_stat_multiplier: float = 1.15
@export var combo_effect_id: String = "bleed" # Ej: Sangrado, Fuego, Parrying
@export var swap_cooldown: float = 1.0 # Pequeño cooldown para evitar spam

func _init() -> void:
	item_type = ItemType.MASK
