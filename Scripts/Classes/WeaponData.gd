class_name WeaponData
extends ItemData

@export var base_damage: float = 20.0
@export var attack_cooldown: float = 0.4
@export var combo_animation_tag: String = "slash"

@export_group("Golpe")
## Alcance en píxeles desde el origen del atacante hasta el final de la zona de golpe.
@export var reach: float = 60.0
## Alto de la zona de golpe.
@export var hit_height: float = 40.0
## Anticipación: segundos desde que se acepta el ataque hasta que puede dañar.
## La animación de ataque reparte sus cuadros de preparación en este tiempo.
@export var startup: float = 0.16
## Ventana activa: segundos durante los que la zona de golpe está abierta.
@export var active_time: float = 0.08
## Recuperación: segundos tras la ventana activa sin poder actuar de nuevo.
@export var recovery: float = 0.16
# attack_cooldown cuenta desde el inicio del ataque hasta poder iniciar otro.

func _init() -> void:
	item_type = ItemType.WEAPON
