class_name ItemCatalog
extends RefCounted

## Registro de IDs estables de objetos. Los puntos de control (y el guardado
## de la etapa 6) guardan estos IDs, nunca nodos ni rutas de escena.
## Un ID nuevo se añade aquí y en el `id` de su recurso.

const PATHS: Dictionary = {
	"copper_sword": "res://Items/Weapons/Copper_Sword_test.tres",
	"test_mace": "res://Items/Weapons/Test_Mace.tres",
	"crypt_mace": "res://Items/Weapons/Crypt_Mace.tres",
	"mask_vow": "res://Items/Masks/Mask_Vow.tres",
	"mask_ember": "res://Items/Masks/Mask_Ember.tres",
}

static func has_item(id: String) -> bool:
	return PATHS.has(id)

## Devuelve el recurso del ID o null si el ID está vacío o es desconocido.
static func get_item(id: String) -> ItemData:
	if id.is_empty():
		return null
	if not PATHS.has(id):
		push_warning("ItemCatalog: ID desconocido '%s'" % id)
		return null
	return load(PATHS[id]) as ItemData
