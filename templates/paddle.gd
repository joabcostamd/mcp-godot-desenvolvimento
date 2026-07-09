## Paddle Controller — Godot 4.7 Style Guide compliant.
##
## CharacterBody2D com movimento vertical (tipo Pong).
## Use com Input Map: move_up, move_down.

class_name PaddleController
{% raw %}extends CharacterBody2D

@export var speed: float = 400.0
{% endraw %}
var _screen_height: float = 0.0


func _ready() -> void:
	_screen_height = get_viewport_rect().size.y


func _physics_process(_delta: float) -> void:
	var direction := Input.get_axis("move_up", "move_down")
	velocity.y = direction * speed
	position.y = clamp(position.y, 60.0, _screen_height - 60.0)
	move_and_slide()
