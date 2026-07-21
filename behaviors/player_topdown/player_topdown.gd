## PlayerTopDown — Controle Top-Down | Godot 4.7.
##
## Node filho de CharacterBody2D que lê input do InputMap
## (ui_up/down/left/right) e aplica velocidade com aceleração/fricção.
## O pai deve chamar move_and_slide() no próprio _physics_process.
##
## @behavior: player_topdown
## @genres: topdown_shooter, roguelike, bullet_hell, puzzle, rpg, generic
## @tutorial: behaviors/player_topdown/README.md

@tool
class_name PlayerTopdown
extends Node

## Velocidade máxima (px/s).
@export var speed: float = 200.0:
	set(v):
		speed = clampf(v, 10.0, 2000.0)

## Taxa de aceleração (px/s²).
@export var acceleration: float = 1000.0:
	set(v):
		acceleration = clampf(v, 10.0, 10000.0)

## Taxa de fricção quando sem input (px/s²).
@export var friction: float = 1000.0:
	set(v):
		friction = clampf(v, 10.0, 10000.0)

## Se false, não processa input nem move.
@export var enabled: bool = true

## Emitido a cada frame com a velocidade atual.
signal velocity_changed(velocity: Vector2)

var _initialized: bool = false
var _current_velocity: Vector2 = Vector2.ZERO


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

	var input_dir := _get_input_vector()

	if input_dir.length_squared() > 0.0:
		# Acelera na direção do input (normalizado para evitar boost diagonal)
		var target := input_dir.normalized() * speed
		_current_velocity = _current_velocity.move_toward(target, acceleration * delta)
	else:
		# Desacelera até zero
		_current_velocity = _current_velocity.move_toward(Vector2.ZERO, friction * delta)

	parent.velocity = _current_velocity
	velocity_changed.emit(_current_velocity)


## Retorna o vetor de input bruto das 4 direções (-1..1 em x e y).
func _get_input_vector() -> Vector2:
	var v := Vector2.ZERO
	if Input.is_action_pressed("ui_right"):
		v.x += 1.0
	if Input.is_action_pressed("ui_left"):
		v.x -= 1.0
	if Input.is_action_pressed("ui_down"):
		v.y += 1.0
	if Input.is_action_pressed("ui_up"):
		v.y -= 1.0
	return v


## Reinicia a velocidade a zero (útil ao trocar de cena ou respawn).
func reset() -> void:
	_current_velocity = Vector2.ZERO
	var parent := get_parent()
	if parent is CharacterBody2D:
		parent.velocity = Vector2.ZERO


## Retorna a velocidade atual (px/s).
func get_velocity() -> Vector2:
	return _current_velocity


## Define a velocidade instantaneamente (ignora aceleração).
func set_velocity(v: Vector2) -> void:
	_current_velocity = v.limit_length(speed)
	var parent := get_parent()
	if parent is CharacterBody2D:
		parent.velocity = _current_velocity


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	var p := get_parent()
	if not p is CharacterBody2D:
		w.append("Parent must be CharacterBody2D for velocity to be applied.")
	return w
