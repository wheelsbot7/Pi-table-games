extends Node2D
@export var score: int

func _on_timer_timeout() -> void:
	var ball_scene = preload("res://red_ball.tscn").instantiate()
	ball_scene.clicked.connect(_on_touch_event.bind())
	add_child(ball_scene)

func _on_touch_event():
	score += 1
	$Score.text = "Score: %s" % score
