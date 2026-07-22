## PlayerController — Controle de Plataforma | Godot 4.7.
##
## Node filho de CharacterBody2D. Movimento horizontal com
## aceleração/fricção, pulo com gravidade e detecção de chão.
## Chama move_and_slide() no parent a cada frame.
##
## @behavior: player_controller
## @genres: platformer, metroidvania, generic
## @tutorial: behaviors/player_controller/README.md

@tool
class_name PlayerController
extends Node

## Velocidade horizontal máxima (px/s).
@export var speed: float = 300.0:
	set(v): speed = clampf(v, 10.0, 2000.0)

## Velocidade vertical do pulo (negativa = para cima).
@export var jump_velocity: float = -400.0:
	set(v): jump_velocity = clampf(v, -2000.0, -50.0)

## Força da gravidade (positiva = para baixo).
@export var gravity: float = 980.0:
	set(v): gravity = clampf(v, 100.0, 5000.0)

## Taxa de aceleração horizontal (px/s²).
@export var acceleration: float = 1000.0:
	set(v): acceleration = clampf(v, 10.0, 10000.0)

## Taxa de fricção horizontal sem input (px/s²).
@export var friction: float = 1000.0:
	set(v): friction = clampf(v, 10.0, 10000.0)

## Posição Y abaixo da qual o jogador morre (0 = desativado).
@export var kill_plane_y: float = 0.0:
	set(v): kill_plane_y = v

## Se false, não processa input nem física.
@export var enabled: bool = true:
	set(v): enabled = v

signal player_died()
signal jumped()

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

	# Gravidade (sempre aplicada, mesmo no chão para is_on_floor funcionar)
	if not body.is_on_floor():
		body.velocity.y += gravity * delta
	else:
		# Pequena força para baixo para manter is_on_floor consistente
		body.velocity.y = minf(body.velocity.y, 10.0)

	# Input horizontal
	var input_dir := Input.get_axis("ui_left", "ui_right")

	if input_dir != 0.0:
		body.velocity.x = move_toward(body.velocity.x, input_dir * speed, acceleration * delta)
	else:
		body.velocity.x = move_toward(body.velocity.x, 0.0, friction * delta)

	# Pulo
	if Input.is_action_just_pressed("ui_accept") and body.is_on_floor():
		body.velocity.y = jump_velocity
		jumped.emit()

	body.move_and_slide()

	# Kill plane
	if kill_plane_y > 0.0 and body.global_position.y > kill_plane_y:
		player_died.emit()


## Reinicia a velocidade a zero.
func reset() -> void:
	var parent := get_parent()
	if parent is CharacterBody2D:
		parent.velocity = Vector2.ZERO


## Retorna a velocidade atual do parent.
func get_velocity() -> Vector2:
	var parent := get_parent()
	if parent is CharacterBody2D:
		return parent.velocity
	return Vector2.ZERO


## Verifica se está no chão.
func is_on_ground() -> bool:
	var parent := get_parent()
	if parent is CharacterBody2D:
		return parent.is_on_floor()
	return false


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	var p := get_parent()
	if not p is CharacterBody2D:
		w.append("Parent must be CharacterBody2D for move_and_slide().")
	if kill_plane_y < 0.0:
		w.append("kill_plane_y is negative — player will never die below screen.")
	return w
