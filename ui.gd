extends Control
signal start_game


func _on_button_pressed() -> void:
	hide()
	start_game.emit()
