class_name InputHints
extends RefCounted

## Nombres en español de las teclas que Godot da en inglés. La fuente no tiene
## flechas, así que se escriben con palabras.
const SPANISH: Dictionary = {
	"Space": "Espacio", "Left": "Izq.", "Right": "Der.", "Up": "Arriba", "Down": "Abajo",
	"Escape": "Esc", "Enter": "Intro", "Backspace": "Retroceso", "Tab": "Tab", "Shift": "Mayús",
}

## Todas las teclas de una acción, separadas por " / ".
static func keys_text(action: StringName) -> String:
	if not InputMap.has_action(action):
		return "?"
	var names: Array[String] = []
	for event in InputMap.action_get_events(action):
		var key := event as InputEventKey
		if key:
			names.append(_name(key))
	return " / ".join(names) if not names.is_empty() else "?"

static func _name(key: InputEventKey) -> String:
	var code: Key = key.keycode
	if key.physical_keycode != KEY_NONE:
		code = key.physical_keycode
		if DisplayServer.get_name() != "headless":
			code = DisplayServer.keyboard_get_keycode_from_physical(code)
	var text := OS.get_keycode_string(code)
	return SPANISH.get(text, text)

## Devuelve el nombre de la primera tecla asignada a una acción del InputMap,
## para que los avisos en pantalla sigan a la configuración real.
static func key_text(action: StringName) -> String:
	if not InputMap.has_action(action):
		return "?"
	for event in InputMap.action_get_events(action):
		var key := event as InputEventKey
		if not key:
			continue
		return _name(key)
	return "?"
