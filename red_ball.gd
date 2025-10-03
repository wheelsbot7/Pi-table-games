extends Sprite2D
signal clicked

func _ready() -> void:
	global_position = Vector2(randi_range(200, 1700), randi_range(200, 800))



func _on_area_2d_input_event(_viewport: Node, event: InputEvent, _shape_idx: int) -> void:
	if event is InputEventMouseButton and event.is_pressed():
		clicked.emit()
		queue_free()
