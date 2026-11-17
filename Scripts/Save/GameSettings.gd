class_name GameSettings
extends RefCounted

## Preferencias del jugador, en un archivo aparte del progreso
## (`settings.cfg`, en la misma carpeta que SaveGame). Sobreviven a reiniciar
## el juego y a empezar una partida nueva.

const FILE: String = "settings.cfg"
const BUSES: Dictionary = {"master": &"Master", "music": &"Music", "sfx": &"SFX"}

## Volumen de cada bus de 0 a 1 (1 = el nivel de mezcla del proyecto).
static var volumes: Dictionary = {"master": 1.0, "music": 1.0, "sfx": 1.0}
static var fullscreen: bool = false
## Destellos suaves y avisos sin parpadeo.
static var reduced_effects: bool = false

static var _base_db: Dictionary = {}

static func path() -> String:
	return SaveGame.directory.path_join(FILE)

## Carga (o usa los valores por defecto si el archivo falta o está dañado) y aplica.
static func load_settings() -> void:
	volumes = {"master": 1.0, "music": 1.0, "sfx": 1.0}
	fullscreen = false
	reduced_effects = false
	var config := ConfigFile.new()
	if config.load(path()) == OK:
		for key in volumes:
			var value: Variant = config.get_value("audio", key, 1.0)
			volumes[key] = clampf(float(value), 0.0, 1.0) if (value is float or value is int) else 1.0
		fullscreen = config.get_value("video", "fullscreen", false) == true
		reduced_effects = config.get_value("accessibility", "reduced_effects", false) == true
	apply()

static func save_settings() -> void:
	var config := ConfigFile.new()
	for key in volumes:
		config.set_value("audio", key, volumes[key])
	config.set_value("video", "fullscreen", fullscreen)
	config.set_value("accessibility", "reduced_effects", reduced_effects)
	DirAccess.make_dir_recursive_absolute(SaveGame.directory)
	config.save(path())

static func apply() -> void:
	for key in BUSES:
		var index := AudioServer.get_bus_index(BUSES[key])
		if index < 0:
			continue
		if not _base_db.has(key):
			_base_db[key] = AudioServer.get_bus_volume_db(index)
		var value: float = volumes[key]
		AudioServer.set_bus_mute(index, value <= 0.001)
		AudioServer.set_bus_volume_db(index, _base_db[key] + linear_to_db(maxf(value, 0.001)))
	if DisplayServer.get_name() != "headless":
		var mode := DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED
		if DisplayServer.window_get_mode() != mode:
			DisplayServer.window_set_mode(mode)

static func set_volume(key: String, value: float) -> void:
	volumes[key] = clampf(value, 0.0, 1.0)
	apply()
	save_settings()

static func set_fullscreen(value: bool) -> void:
	fullscreen = value
	apply()
	save_settings()

static func set_reduced_effects(value: bool) -> void:
	reduced_effects = value
	save_settings()

## Intensidad del destello blanco al recibir un golpe.
static func flash_strength() -> float:
	return 1.3 if reduced_effects else 2.0

static func flash_color() -> Color:
	var f := flash_strength()
	return Color(f, f, f)
