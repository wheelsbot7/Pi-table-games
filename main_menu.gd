extends VBoxContainer
var ball_game_scene = preload("res://Ball-Game.tscn").instantiate()



func _on_button_3_pressed() -> void:
	get_tree().quit()



func _on_button_pressed() -> void:
	get_tree().root.add_child(ball_game_scene)
	hide()
