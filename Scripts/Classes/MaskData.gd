class_name MaskData
extends ItemData

## Qué multiplica passive_stat_multiplier. Cada efecto se aplica en un único
## lugar: DAMAGE_TAKEN en Health.take_damage (vía PlayerInventory) y
## WEAPON_DAMAGE al aceptar un ataque (Player.execute_attack).
enum Effect {
	NONE,
	DAMAGE_TAKEN,  ## Multiplica el daño que recibe quien la lleva.
	WEAPON_DAMAGE, ## Multiplica el daño de arma, fijado al iniciar el ataque.
}

@export var effect: Effect = Effect.NONE
@export var passive_stat_multiplier: float = 1.15
## Texto breve para el HUD y el aviso del pickup.
@export var description: String = ""
@export var combo_effect_id: String = "bleed" # Ej: Sangrado, Fuego, Parrying (sin uso todavía)
@export var swap_cooldown: float = 1.0 # Pequeño cooldown para evitar spam

func _init() -> void:
	item_type = ItemType.MASK

func damage_taken_multiplier() -> float:
	return passive_stat_multiplier if effect == Effect.DAMAGE_TAKEN else 1.0

func weapon_damage_multiplier() -> float:
	return passive_stat_multiplier if effect == Effect.WEAPON_DAMAGE else 1.0
