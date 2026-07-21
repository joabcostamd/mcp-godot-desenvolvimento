## PlayerVehicle — Controle de Veículo | Godot 4.7.
##
## Node filho de CharacterBody2D. Movimento baseado em rotação:
## ui_left/right gira, ui_up acelera na direção frontal, ui_down ré.
## Drift reduz velocidade lateral para simular aderência.
##
## @behavior: player_vehicle
## @genres: topdown_shooter, racing, generic
## @tutorial: behaviors/player_vehicle/README.md

@tool
class_name PlayerVehicle
extends Node

## Força de impulso (px/s²).
@export var acceleration: float = 500.0:
	set(v): acceleration = clampf(v, 10.0, 5000.0)

## Velocidade máxima (px/s).
@export var max_speed: float = 400.0:
	set(v): max_speed = clampf(v, 10.0, 3000.0)

## Velocidade de rotação (rad/s).
@export var turn_rate: float = 3.0:
	set(v): turn_rate = clampf(v, 0.5, 20.0)

## Fricção lateral (0 = drift livre, 1 = zero drift).
@export var drift: float = 0.9:
	set(v): drift = clampf(v, 0.0, 1.0)

## Se false, não processa input.
@export var enabled: bool = true

var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_initialized = true


func _physics_process(delta: float) -> void:
	if not enabled:
		return

	var parent := get_parent()
	if not parent is CharacterBody2D:
		return

	var body := parent as CharacterBody2D

	# Rotação
	var turn_input := Input.get_axis("ui_left", "ui_right")
	body.rotation += turn_input * turn_rate * delta

	# Impulso na direção frontal
	var thrust := Input.get_axis("ui_down", "ui_up")  # up = 1, down = -1
	if thrust != 0.0:
		var forward := Vector2.RIGHT.rotated(body.rotation)
		body.velocity += forward * thrust * acceleration * delta

	# Limita velocidade máxima
	if body.velocity.length() > max_speed:
		body.velocity = body.velocity.normalized() * max_speed

	# Drift: reduz velocidade lateral (perpendicular à direção frontal)
	var forward := Vector2.RIGHT.rotated(body.rotation)
	var forward_vel := forward.dot(body.velocity) * forward
	var lateral_vel := body.velocity - forward_vel
	body.velocity = forward_vel + lateral_vel * (1.0 - drift)

	body.move_and_slide()


## Reinicia a velocidade a zero.
func reset() -> void:
	var parent := get_parent()
	if parent is CharacterBody2D:
		parent.velocity = Vector2.ZERO


## Retorna a velocidade atual.
func get_velocity() -> Vector2:
	var parent := get_parent()
	if parent is CharacterBody2D:
		return parent.velocity
	return Vector2.ZERO
