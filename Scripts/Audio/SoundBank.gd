class_name SoundBank
extends RefCounted

## Efectos cortos del juego en el bus "SFX". Cada sonido refuerza una señal
## que ya es visible (pose, destello, HUD): nada depende sólo del audio.
## Se cargan bajo demanda: un archivo que aún no existe simplemente no suena.

const PATHS: Dictionary = {
	&"attack": "res://Audio/sfx_attack.wav",
	&"hit": "res://Audio/sfx_hit.wav",
	&"pickup": "res://Audio/sfx_pickup.wav",
	&"mask": "res://Audio/sfx_mask.wav",
	&"throw": "res://Audio/sfx_throw.wav",
	&"tell_sweep": "res://Audio/sfx_tell_sweep.wav",
	&"tell_rain": "res://Audio/sfx_tell_rain.wav",
	&"roar": "res://Audio/sfx_roar.wav",
	&"checkpoint": "res://Audio/sfx_checkpoint.wav",
	&"ember_impact": "res://Audio/sfx_ember_impact.wav",
}

static var _cache: Dictionary = {}

static func stream(id: StringName) -> AudioStream:
	if not _cache.has(id):
		var path: String = PATHS.get(id, "")
		_cache[id] = load(path) if not path.is_empty() and ResourceLoader.exists(path) else null
	return _cache[id]

## Reproduce `id` una vez. El reproductor cuelga de la raíz para sobrevivir a
## un cambio de sala y se libera al terminar. En headless no suena nada.
static func play(from: Node, id: StringName, pitch: float = 1.0) -> void:
	if not from.is_inside_tree() or DisplayServer.get_name() == "headless":
		return
	var sound := stream(id)
	if not sound:
		return
	var player := AudioStreamPlayer.new()
	player.stream = sound
	player.bus = &"SFX"
	player.pitch_scale = pitch
	player.finished.connect(player.queue_free)
	from.get_tree().root.add_child(player)
	player.play()
