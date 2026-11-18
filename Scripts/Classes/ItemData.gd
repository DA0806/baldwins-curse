class_name ItemData
extends Resource

enum ItemType { WEAPON, MASK }

@export var id: String = ""
@export var name: String = ""
@export var icon: Texture2D
## Pixel-sized world art; external resources may keep using their HUD icon as fallback.
@export var world_texture: Texture2D
@export_range(0.1, 4.0, 0.05) var world_scale: float = 1.0
@export var item_type: ItemType = ItemType.WEAPON
