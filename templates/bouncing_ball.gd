## Bouncing Ball — Godot 4.7 Style Guide compliant.
##
## RigidBody2D que quica mantendo velocidade constante.
## Use para bola de Pong, Breakout, ou projeteis fisicos.

class_name BouncingBall
{% raw %}extends RigidBody2D

@export var initial_speed: float = 300.0
{% endraw %}
var _speed: float = 0.0


func _ready() -> void:
	_speed = initial_speed
	var direction := Vector2.RIGHT.rotated(randf_range(-0.5, 0.5))
	linear_velocity = direction * _speed


func _physics_process(_delta: float) -> void:
	linear_velocity = linear_velocity.normalized() * _speed


func reset_ball() -> void:
	position = Vector2.ZERO
	var direction := Vector2.RIGHT.rotated(randf_range(-0.5, 0.5))
	linear_velocity = direction * _speed
