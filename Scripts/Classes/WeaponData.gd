class_name WeaponData
extends ItemData

@export var base_damage: float = 20.0
@export var attack_cooldown: float = 0.4
@export var combo_animation_tag: String = "slash"

func _init() -> void:
	item_type = ItemType.WEAPON
