class_name ItemData
extends Resource

enum ItemType { WEAPON, MASK }

@export var id: String = ""
@export var name: String = ""
@export var icon: Texture2D
@export var item_type: ItemType = ItemType.WEAPON
