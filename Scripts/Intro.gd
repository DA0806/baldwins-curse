extends Control

## Plano de entrada: la motivación de Baldwin en una imagen y tres frases.
## Cualquier tecla de acción empieza la partida en el Atrio.

const ART := "res://Sprites/Story/intro.png"

@onready var picture: TextureRect = $Picture
@onready var story: Label = $Story
@onready var prompt: Label = $Prompt

func _ready() -> void:
	if ResourceLoader.exists(ART):
		picture.texture = load(ART)
	prompt.text = "[%s] Comenzar" % InputHints.key_text(&"interact")
	story.modulate.a = 0.0
	prompt.modulate.a = 0.0
	var tween := create_tween()
	tween.tween_property(story, "modulate:a", 1.0, 1.2)
	tween.tween_property(prompt, "modulate:a", 1.0, 0.5)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_echo():
		return
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept") or event.is_action_pressed("jump"):
		get_viewport().set_input_as_handled()
		RunSession.of(self).new_run()
