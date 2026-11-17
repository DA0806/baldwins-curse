class_name PauseMenu
extends CanvasLayer

## Menú de pausa. Funciona con el árbol en pausa (PROCESS_MODE_ALWAYS); el
## mundo, el jugador y sus ataques no reciben entradas mientras está abierto.

var menu: MenuPanel

func _ready() -> void:
	layer = 60
	process_mode = Node.PROCESS_MODE_ALWAYS
	var dim := ColorRect.new()
	dim.color = Color(0.082, 0.098, 0.141, 0.6)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var session := RunSession.of(self)
	menu = MenuPanel.new()
	add_child(menu)
	menu.add_title("Pausa")
	menu.add_button("Reanudar", session.resume_game)
	var checkpoint := menu.add_button("Volver al último brasero", session.restart_from_checkpoint)
	checkpoint.disabled = session.checkpoint.is_empty()
	menu.add_button("Ajustes", func(): MenuPanels.open_over(self, menu, MenuPanels.settings()))
	menu.add_button("Controles", func(): MenuPanels.open_over(self, menu, MenuPanels.controls()))
	menu.add_button("Volver al título", session.go_to_title)
	menu.add_text("El progreso se guarda al encender cada brasero.", 9, MenuPanel.MUTED)
	# Esc en el menú principal de la pausa reanuda.
	menu.closed.connect(session.resume_game)
