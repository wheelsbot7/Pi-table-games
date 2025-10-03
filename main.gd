extends Node

@onready var ball_scene: PackedScene
var score

func _on_control_start_game() -> void:
	$Timer.start()
	score = 0


func _on_timer_timeout() -> void:
	spawn_ball()


func spawn_ball() -> void:
	var ball = ball_scene.instantiate()
	ball.rotation = randf()
	ball.scale.x = 0.1
	ball.scale.y = 0.1
	ball.position.x = randf_range(200,1720)
	ball.position.y = randf_range(200,880)
	ball.clicked.connect(score_up)
	
	add_child(ball)

func score_up():
	score += 1
	$Score.text = "Score: %s" % score
