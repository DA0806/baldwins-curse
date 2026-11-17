extends Label

## Texto de tutorial. Cada {acción} se sustituye por su tecla del InputMap,
## así que el texto sigue siendo correcto si cambian los controles.

func _ready() -> void:
	var result: String = text
	for action in InputMap.get_actions():
		var token: String = "{%s}" % action
		if result.contains(token):
			result = result.replace(token, InputHints.key_text(action))
	text = result
