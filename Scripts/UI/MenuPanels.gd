class_name MenuPanels
extends RefCounted

## Pantallas secundarias compartidas por el título y la pausa: ajustes,
## controles, créditos y confirmación.

const VOLUME_LABELS: Dictionary = {"master": "Volumen general", "music": "Música y ambiente", "sfx": "Efectos"}

## Abre `panel` sobre `menu` (que se oculta) y, al cerrarlo, devuelve el foco
## al control que lo tenía al abrir (el botón pulsado).
static func open_over(parent: Node, menu: Control, panel: MenuPanel) -> MenuPanel:
	var focus_back := menu.get_viewport().gui_get_focus_owner()
	menu.visible = false
	parent.add_child(panel)
	panel.closed.connect(func():
		menu.visible = true
		if is_instance_valid(focus_back):
			focus_back.grab_focus())
	return panel

static func settings() -> MenuPanel:
	var panel := MenuPanel.new()
	panel.add_title("Ajustes")
	for key in ["master", "music", "sfx"]:
		_add_volume(panel, key)
	var fullscreen := CheckButton.new()
	fullscreen.text = "Pantalla completa"
	fullscreen.button_pressed = GameSettings.fullscreen
	fullscreen.toggled.connect(GameSettings.set_fullscreen)
	panel.box.add_child(fullscreen)
	var reduced := CheckButton.new()
	reduced.text = "Efectos reducidos"
	reduced.button_pressed = GameSettings.reduced_effects
	reduced.toggled.connect(GameSettings.set_reduced_effects)
	panel.box.add_child(reduced)
	panel.add_text("Destellos más suaves y avisos sin parpadeo. El peligro se sigue leyendo por la forma.", 9, MenuPanel.MUTED, 280.0)
	panel.add_button("Volver", panel.close)
	return panel

static func _add_volume(panel: MenuPanel, key: String) -> void:
	var row := HBoxContainer.new()
	var name := Label.new()
	name.text = VOLUME_LABELS[key]
	name.custom_minimum_size.x = 120
	name.add_theme_font_size_override("font_size", 11)
	var slider := HSlider.new()
	slider.name = "Volume_" + key
	slider.min_value = 0
	slider.max_value = 100
	slider.step = 5
	slider.value = roundf(GameSettings.volumes[key] * 100.0)
	slider.custom_minimum_size = Vector2(110, 16)
	slider.focus_mode = Control.FOCUS_ALL
	var value := Label.new()
	value.text = "%d %%" % slider.value
	value.custom_minimum_size.x = 40
	value.add_theme_font_size_override("font_size", 11)
	slider.value_changed.connect(func(v: float):
		value.text = "%d %%" % v
		GameSettings.set_volume(key, v / 100.0))
	# El foco del deslizador se marca en su etiqueta: brasa y un punto delante.
	slider.focus_entered.connect(func():
		name.add_theme_color_override("font_color", MenuPanel.EMBER)
		name.text = "• " + VOLUME_LABELS[key])
	slider.focus_exited.connect(func():
		name.remove_theme_color_override("font_color")
		name.text = VOLUME_LABELS[key])
	row.add_child(name)
	row.add_child(slider)
	row.add_child(value)
	panel.box.add_child(row)
	panel.remember_focus(slider)

static func controls() -> MenuPanel:
	var panel := MenuPanel.new()
	panel.add_title("Controles")
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 16)
	grid.add_theme_constant_override("v_separation", 3)
	var rows := [
		["Caminar", [&"move_left", &"move_right"]],
		["Saltar (mantener: más alto)", [&"jump"]],
		["Recoger o intercambiar", [&"interact"]],
		["Atacar con la ranura 1", [&"attack_weapon_1"]],
		["Atacar con la ranura 2", [&"attack_weapon_2"]],
		["Máscara anterior / siguiente", [&"prev_mask", &"next_mask"]],
		["Pausa", [&"pause"]],
	]
	for row in rows:
		var action := Label.new()
		action.text = row[0]
		action.add_theme_font_size_override("font_size", 11)
		var keys := Label.new()
		keys.text = " · ".join(row[1].map(func(a): return InputHints.keys_text(a)))
		keys.add_theme_font_size_override("font_size", 11)
		keys.add_theme_color_override("font_color", MenuPanel.EMBER)
		grid.add_child(action)
		grid.add_child(keys)
	panel.box.add_child(grid)
	panel.add_text("Menús: flechas para moverse, Intro o Espacio para aceptar, Esc para volver.", 9, MenuPanel.MUTED, 300.0)
	panel.add_button("Volver", panel.close)
	return panel

static func credits() -> MenuPanel:
	var panel := MenuPanel.new()
	panel.add_title("Créditos")
	panel.add_text("Baldwin's Curse", 12, MenuPanel.EMBER)
	panel.add_text("Proyecto original: Diego Arau Andreu (DA0806).", 10)
	panel.add_text("Arte, sonido y escenarios generados por código para este proyecto (tools/gen_atrio_assets.py y tools/gen_zone_assets.py).", 10, MenuPanel.IVORY, 300.0)
	panel.add_text("Hecho con Godot Engine (licencia MIT, godotengine.org).", 10)
	panel.add_text("Procedencia de cada recurso: docs/assets.md.", 9, MenuPanel.MUTED)
	panel.add_button("Volver", panel.close)
	return panel

## Confirmación con "No" enfocado por defecto. `on_yes` sólo se llama al aceptar.
static func confirm(title: String, message: String, yes_text: String, on_yes: Callable) -> MenuPanel:
	var panel := MenuPanel.new()
	panel.add_title(title)
	panel.add_text(message, 11, MenuPanel.IVORY, 300.0)
	panel.add_button("No, volver", panel.close)
	panel.add_button(yes_text, func():
		panel.close()
		on_yes.call())
	return panel
