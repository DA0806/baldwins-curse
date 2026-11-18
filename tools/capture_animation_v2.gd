extends "res://tools/capture_prerendered.gd"

# Save the same campaign checkpoints separately for the independent-equipment pass.
func _save(name: String) -> void:
	paused = true
	if is_instance_valid(player):
		player.sprite.modulate = Color.WHITE
		player.presentation.sync_pose()
	for enemy in get_nodes_in_group("enemies"):
		if enemy is CanvasItem:
			enemy.modulate = Color.WHITE
	await _frames(3)
	var output := "res://docs/animation_v2/capturas/"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output))
	root.get_texture().get_image().save_png(ProjectSettings.globalize_path(output + name + ".png"))
	paused = false
