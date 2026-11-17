class_name MenuPanel
extends CenterContainer

## Base de las pantallas de menú: un panel centrado con título, textos y
## botones, navegable sólo con teclado (flechas, Intro/Espacio para aceptar,
## Esc para volver). El primer control que se añade recibe el foco.

signal closed

const EMBER := Color("f0a758")
const IVORY := Color("e5d6b3")
const MUTED := Color("a99c80")

## Si es false, Esc no cierra el panel (menú principal del título).
var cancellable: bool = true
var box: VBoxContainer
var _first_focus: Control

func _init() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	process_mode = Node.PROCESS_MODE_ALWAYS
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.082, 0.098, 0.141, 0.94)
	style.border_color = EMBER
	style.set_border_width_all(2)
	style.set_corner_radius_all(2)
	style.set_content_margin_all(14)
	var panel := PanelContainer.new()
	panel.add_theme_stylebox_override("panel", style)
	add_child(panel)
	box = VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	panel.add_child(box)

func _ready() -> void:
	focus_first.call_deferred()

func add_title(text: String) -> Label:
	var label := add_text(text, 16, EMBER)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	return label

func add_text(text: String, size: int = 11, color: Color = IVORY, width: float = 0.0) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	if width > 0.0:
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		label.custom_minimum_size.x = width
	box.add_child(label)
	return label

func add_button(text: String, callback: Callable) -> Button:
	var button := Button.new()
	button.text = text
	button.custom_minimum_size = Vector2(230, 0)
	button.focus_mode = Control.FOCUS_ALL
	button.pressed.connect(callback)
	box.add_child(button)
	remember_focus(button)
	return button

func remember_focus(control: Control) -> void:
	if not _first_focus:
		_first_focus = control

func focus_first() -> void:
	if is_instance_valid(_first_focus) and _first_focus.is_visible_in_tree() and _first_focus.focus_mode != Control.FOCUS_NONE:
		_first_focus.grab_focus()

func close() -> void:
	closed.emit()
	queue_free()

func _unhandled_input(event: InputEvent) -> void:
	if not cancellable or not is_visible_in_tree():
		return
	if event.is_action_pressed("ui_cancel") or event.is_action_pressed("pause"):
		get_viewport().set_input_as_handled()
		close()
