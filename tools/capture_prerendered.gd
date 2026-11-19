extends "res://tools/stage5_capture.gd"

## Capture runs never write a player's save slot.
func _initialize() -> void:
	_capture()

## Autoloads are available on the first process frame.
func _capture() -> void:
	await process_frame
	root.get_node("GameSession").save_enabled = false
	_run()

## Reuses campaign staging while preserving the previous milestone screenshots.
func _save(name: String) -> void:
	paused = true
	if is_instance_valid(player):
		player.sprite.modulate = Color.WHITE
	for enemy in get_nodes_in_group("enemies"):
		if enemy is CanvasItem:
			enemy.modulate = Color.WHITE
	await _frames(3)
	var output := "res://docs/prerendered/capturas/"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output))
	root.get_texture().get_image().save_png(ProjectSettings.globalize_path(output + name + ".png"))
	paused = false
