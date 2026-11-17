extends Control

## Epílogo de victoria: se activa al cruzar la salida tras vencer al Abad.
## Muestra el desenlace, el tiempo y los reintentos, y devuelve al inicio de la
## campaña (en la etapa 6, al menú).

const ART := "res://Sprites/Story/epilogue.png"

@onready var picture: TextureRect = $Picture
@onready var stats: Label = $Stats
@onready var prompt: Label = $Prompt

func _ready() -> void:
	if ResourceLoader.exists(ART):
		picture.texture = load(ART)
	var session := RunSession.of(self)
	var seconds: int = int(session.run_time)
	stats.text = "Tiempo %d:%02d · Reintentos %d" % [seconds / 60, seconds % 60, session.retries]
	prompt.text = "[%s] Volver al título" % InputHints.key_text(&"interact")

func _unhandled_input(event: InputEvent) -> void:
	if event.is_echo():
		return
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		get_viewport().set_input_as_handled()
		RunSession.of(self).go_to_title()
