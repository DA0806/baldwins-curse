class_name SaveGame
extends RefCounted

## Progreso guardado: una sola ranura con la última activación de un punto de
## control, en JSON versionado dentro de user://. Sólo guarda IDs estables (sala,
## punto de aparición, objetos, recogidas únicas), nunca nodos.
##
## Escritura segura: se escribe `savegame.json.tmp`, la versión anterior pasa a
## `savegame.json.bak` y el temporal ocupa su sitio. Si al leer el principal
## falta o está dañado, se intenta el .bak.
##
##   {"format": "baldwins-curse-save", "version": 1, "saved_at": 1763380000,
##    "completed": false, "run_time": 754.2, "retries": 3,
##    "checkpoint": {<contrato de GameSession>}}

const FORMAT: String = "baldwins-curse-save"
const VERSION: int = 1
const FILE: String = "savegame.json"
const ZONES: Dictionary = {"atrio": "Atrio del Voto", "cripta": "Cripta de las Ascuas", "capilla": "Capilla del Último Sello"}

enum Status { OK, MISSING, CORRUPT, INCOMPATIBLE, UNKNOWN_ROOM }

## Carpeta de guardado y preferencias. Las pruebas la cambian para no tocar la
## partida real del jugador.
static var directory: String = "user://"

class LoadResult:
	var status: int = Status.MISSING
	var data: Dictionary = {}
	## IDs de objetos que ya no existen y se omitieron al cargar.
	var dropped_ids: Array[String] = []
	var from_backup: bool = false

	func exists() -> bool:
		return status != Status.MISSING

	func completed() -> bool:
		return status == Status.OK and bool(data.get("completed", false))

	func can_continue() -> bool:
		return status == Status.OK and not completed()

	## Texto para el título: siempre dice en qué estado está el archivo.
	func message() -> String:
		match status:
			Status.MISSING:
				return "No hay partida guardada."
			Status.CORRUPT:
				return "La partida guardada está dañada y no se puede cargar."
			Status.INCOMPATIBLE:
				var version: Variant = data.get("version", "?")
				if version is float and version == floorf(version):
					version = int(version)
				return "La partida guardada es de otra versión (%s) y no se puede cargar." % str(version)
			Status.UNKNOWN_ROOM:
				return "La partida guardada apunta a una sala que ya no existe."
		var text: String
		var time := SaveGame.format_time(float(data.get("run_time", 0.0)))
		if completed():
			text = "Partida completada · %s · %d reintentos" % [time, int(data.get("retries", 0))]
		else:
			text = "Último brasero: %s · %s" % [SaveGame.zone_name(String(data.checkpoint.room_id)), time]
		if not dropped_ids.is_empty():
			text += "\nSe omitieron objetos que ya no existen."
		if from_backup:
			text += "\nRecuperada de la copia de seguridad."
		return text

static func path() -> String:
	return directory.path_join(FILE)

static func format_time(seconds: float) -> String:
	var total := int(seconds)
	return "%d:%02d" % [total / 60, total % 60]

static func zone_name(room_id: String) -> String:
	return ZONES.get(room_id.get_slice("_", 0), room_id)

## Guarda el estado de la partida. Devuelve false si no se pudo escribir.
static func write(session: Node) -> bool:
	return write_data({
		"format": FORMAT,
		"version": VERSION,
		"saved_at": int(Time.get_unix_time_from_system()),
		"completed": session.finished,
		"run_time": session.run_time,
		"retries": session.retries,
		"checkpoint": session.checkpoint,
	})

static func write_data(data: Dictionary) -> bool:
	DirAccess.make_dir_recursive_absolute(directory)
	var main := path()
	var tmp := main + ".tmp"
	var backup := main + ".bak"
	var file := FileAccess.open(tmp, FileAccess.WRITE)
	if not file:
		push_warning("SaveGame: no se pudo escribir %s" % tmp)
		return false
	file.store_string(JSON.stringify(data, "\t"))
	file.close()
	if FileAccess.file_exists(main):
		if FileAccess.file_exists(backup):
			DirAccess.remove_absolute(backup)
		DirAccess.rename_absolute(main, backup)
	return DirAccess.rename_absolute(tmp, main) == OK

static func delete_all() -> void:
	for suffix in ["", ".tmp", ".bak"]:
		if FileAccess.file_exists(path() + suffix):
			DirAccess.remove_absolute(path() + suffix)

static func load_game() -> LoadResult:
	var result := read(path())
	if result.status == Status.MISSING or result.status == Status.CORRUPT:
		var backup := read(path() + ".bak")
		if backup.status == Status.OK:
			backup.from_backup = true
			return backup
	return result

## Lee y valida un archivo. Nunca lanza: cualquier problema es un estado.
static func read(file_path: String) -> LoadResult:
	var result := LoadResult.new()
	if not FileAccess.file_exists(file_path):
		return result
	result.status = Status.CORRUPT
	var json := JSON.new()
	if json.parse(FileAccess.get_file_as_string(file_path)) != OK:
		return result
	var parsed: Variant = json.data
	if not parsed is Dictionary or parsed.get("format") != FORMAT:
		return result
	var data: Dictionary = parsed
	if not (data.get("version") is float or data.get("version") is int):
		return result
	if int(data.version) != VERSION:
		result.status = Status.INCOMPATIBLE
		result.data = data
		return result
	var checkpoint: Variant = data.get("checkpoint")
	if not checkpoint is Dictionary or not checkpoint.get("room_id") is String or not checkpoint.get("spawn_id") is String \
			or not checkpoint.get("inventory") is Dictionary or not checkpoint.get("collected") is Array:
		return result
	if not RunSession.ROOMS.has(checkpoint.room_id):
		result.status = Status.UNKNOWN_ROOM
		result.data = data
		return result
	_clean_inventory(checkpoint.inventory, result.dropped_ids)
	checkpoint.health = maxf(1.0, float(checkpoint.get("health", 100.0)))
	result.status = Status.OK
	result.data = data
	return result

## Quita del inventario los IDs que ya no existen en ItemCatalog.
static func _clean_inventory(inventory: Dictionary, dropped: Array[String]) -> void:
	var weapons: Array = inventory.get("weapons", [])
	for i in weapons.size():
		var id := String(weapons[i])
		if not id.is_empty() and not ItemCatalog.has_item(id):
			dropped.append(id)
			weapons[i] = ""
	var masks: Array = []
	for id in inventory.get("masks", []):
		if ItemCatalog.has_item(String(id)):
			masks.append(String(id))
		else:
			dropped.append(String(id))
	inventory.weapons = weapons
	inventory.masks = masks
