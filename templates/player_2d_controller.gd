## Player 2D Controller — Godot 4.7 Style Guide compliant.
##
## CharacterBody2D com movimento horizontal, pulo e gravidade.
## Use com Input Map: move_left, move_right, jump.
##
## @behavior: player_controller
## @genres: platformer, metroidvania
## @tutorial: templates/player_2d_controller.gd

class_name PlayerController
{% raw %}extends CharacterBody2D

signal player_died()

const GRAVITY: float = 980.0

@export var speed: float = 300.0
@export var jump_velocity: float = -400.0
{% endraw %}

func _physics_process(delta: float) -> void:
	# Gravity
	if not is_on_floor():
		velocity.y += GRAVITY * delta

	# Jump
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_velocity

	# Horizontal movement
	var direction := Input.get_axis("move_left", "move_right")
	if direction != 0.0:
		velocity.x = direction * speed
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed)

	move_and_slide()
