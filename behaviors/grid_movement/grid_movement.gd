## GridMovement — Movimento em Grid | Godot 4.7.
##
## Node filho de Node2D. Movimento discreto em passos de grid_size.
## Tween interpola posição. Bloqueia input durante movimento.
##
## @behavior: grid_movement
## @genres: roguelike, puzzle, generic
## @tutorial: behaviors/grid_movement/README.md

@tool
class_name GridMovement
extends Node

## Tamanho da célula em pixels.
@export var grid_size: Vector2 = Vector2(32, 32):
	set(v):
		grid_size = Vector2(maxf(v.x, 4.0), maxf(v.y, 4.0))

## Duração da animação (s).
@export var move_duration: float = 0.15:
	set(v):
		move_duration = clampf(v, 0.01, 1.0)

## Ajusta posição inicial para grid.
@export var snap_on_start: bool = true

## Se false, não processa input.
@export var enabled: bool = true

signal moved(direction: Vector2)
signal arrived(grid_pos: Vector2)

var _moving: bool = false
var _target_position: Vector2 = Vector2.ZERO
var _tween: Tween
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	if snap_on_start:
		_snap_to_grid()
	_initialized = true


func _physics_process(_delta: float) -> void:
	if not enabled or _moving:
		return

	var parent := get_parent()
	if not parent is Node2D:
		return

	var input_dir := _get_grid_input()
	if input_dir.length_squared() < 0.01:
		return

	var body := parent as Node2D
	var target := body.position + input_dir * grid_size
	_move_to(body, target, input_dir)


func _get_grid_input() -> Vector2:
	var v := Vector2.ZERO
	if Input.is_action_just_pressed("ui_right"): v.x += 1
	if Input.is_action_just_pressed("ui_left"): v.x -= 1
	if Input.is_action_just_pressed("ui_down"): v.y += 1
	if Input.is_action_just_pressed("ui_up"): v.y -= 1
	return v


func _move_to(body: Node2D, target: Vector2, direction: Vector2) -> void:
	_moving = true
	_target_position = target

	if _tween and _tween.is_valid():
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(body, "position", target, move_duration)
	_tween.tween_callback(_on_arrive)

	moved.emit(direction)


func _on_arrive() -> void:
	_moving = false
	arrived.emit(_target_position)


func _snap_to_grid() -> void:
	var parent := get_parent()
	if not parent is Node2D:
		return
	var p := (parent as Node2D).position
	var snapped := Vector2(
		round(p.x / grid_size.x) * grid_size.x,
		round(p.y / grid_size.y) * grid_size.y
	)
	(parent as Node2D).position = snapped


## Força movimento para uma posição de grid.
func move_to_grid(grid_x: int, grid_y: int) -> void:
	if _moving:
		return
	var parent := get_parent()
	if not parent is Node2D:
		return
	var target := Vector2(grid_x * grid_size.x, grid_y * grid_size.y)
	_move_to(parent as Node2D, target, (target - (parent as Node2D).position).normalized())


## Retorna true se está em movimento.
func is_moving() -> bool:
	return _moving


## Retorna a posição de grid atual (coluna, linha).
func get_grid_position() -> Vector2:
	var parent := get_parent()
	if not parent is Node2D:
		return Vector2.ZERO
	var p := (parent as Node2D).position
	return Vector2(round(p.x / grid_size.x), round(p.y / grid_size.y))


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	var p := get_parent()
	if not p is Node2D:
		w.append("Parent must be Node2D for grid movement to work.")
	if grid_size.x < 8.0 or grid_size.y < 8.0:
		w.append("grid_size is very small — movement may look choppy.")
	return w
