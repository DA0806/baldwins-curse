extends Control

## Pantalla de título: continuar, nueva partida, ajustes, controles, créditos y
## salir. Siempre dice en qué estado está la partida guardada (falta, dañada,
## otra versión, sala inexistente, completada) y sigue operativa en todos ellos.

const ART := "res://Sprites/Story/intro.png"
const AMBIENCE := "res://Audio/amb_atrio.wav"

var menu: MenuPanel
var status: Label
var continue_button: Button
var save: SaveGame.LoadResult

func _ready() -> void:
	var session := RunSession.of(self)
	var background := ColorRect.new()
	background.color = Color(0.082, 0.098, 0.141)
	background.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(background)
	if ResourceLoader.exists(ART):
		var picture := TextureRect.new()
		picture.texture = load(ART)
		picture.set_anchors_preset(Control.PRESET_FULL_RECT)
		picture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		picture.modulate = Color(0.45, 0.45, 0.5)
		add_child(picture)
	var title := _label("Baldwin's Curse", 22, MenuPanel.EMBER, 14)
	title.name = "Title"
	status = _label("", 10, MenuPanel.IVORY, 44)
	status.name = "SaveStatus"

	save = SaveGame.load_game()
	status.text = save.message()

	menu = MenuPanel.new()
	menu.cancellable = false
	menu.position.y = 30
	add_child(menu)
	continue_button = menu.add_button("Continuar", _on_continue)
	continue_button.disabled = not save.can_continue()
	var new_game := menu.add_button("Nueva partida", _on_new_game)
	menu.add_button("Ajustes", func(): MenuPanels.open_over(self, menu, MenuPanels.settings()))
	menu.add_button("Controles", func(): MenuPanels.open_over(self, menu, MenuPanels.controls()))
	menu.add_button("Créditos", func(): MenuPanels.open_over(self, menu, MenuPanels.credits()))
	menu.add_button("Salir", func(): get_tree().quit())
	# Foco inicial: Continuar si se puede; si no, Nueva partida.
	menu._first_focus = continue_button if save.can_continue() else new_game
	if ResourceLoader.exists(AMBIENCE):
		session.set_ambience(load(AMBIENCE))

func _label(text: String, size: int, color: Color, top: float) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.set_anchors_preset(Control.PRESET_TOP_WIDE)
	label.offset_top = top
	add_child(label)
	return label

func _on_continue() -> void:
	RunSession.of(self).continue_game()

## Con una partida guardada (válida o no), pide confirmación: hay una sola ranura.
func _on_new_game() -> void:
	if not save.exists():
		RunSession.of(self).start_campaign()
		return
	var what := "la partida guardada (%s)" % save.message().get_slice("\n", 0) if save.status == SaveGame.Status.OK \
		else "el archivo de partida actual, que no se puede cargar"
	MenuPanels.open_over(self, menu, MenuPanels.confirm("Nueva partida",
		"Sólo hay una ranura de guardado: empezar de nuevo sustituirá %s." % what,
		"Sí, empezar de nuevo", func(): RunSession.of(self).start_campaign()))
