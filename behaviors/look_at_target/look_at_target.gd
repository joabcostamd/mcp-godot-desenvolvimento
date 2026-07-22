## LookAtTarget — Mirar Alvo | Godot 4.7.
##
## Node que rotaciona o parent Node2D para mirar um alvo.
## Suporta alvo Node2D ou posição fixa. Offset angular.
##
## @behavior: look_at_target
## @genres: generic

@tool
class_name LookAtTarget
extends Node

@export var rotation_speed: float = 5.0:
	set(v): rotation_speed = clampf(v, 0.0, 50.0)
@export var angle_offset: float = 0.0

signal target_acquired(target: Node2D)
signal target_lost()

var _target: Node2D = null
var _target_position: Vector2 = Vector2.ZERO
var _use_position: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_initialized = true


func _physics_process(delta: float) -> void:
	var parent := get_parent()
	if not parent is Node2D: return

	var target_pos := _get_target_pos()
	if target_pos == Vector2.INF: return

	var p := parent as Node2D
	var desired := p.global_position.direction_to(target_pos).angle() + angle_offset

	if rotation_speed <= 0.0:
		p.rotation = desired
	else:
		p.rotation = lerp_angle(p.rotation, desired, rotation_speed * delta)


func _get_target_pos() -> Vector2:
	if _target and is_instance_valid(_target):
		return _target.global_position
	if _use_position:
		return _target_position
	return Vector2.INF


func set_target(node: Node2D) -> void:
	_target = node
	_use_position = false
	target_acquired.emit(node)


func set_target_position(pos: Vector2) -> void:
	_target_position = pos
	_use_position = true
	_target = null


func clear_target() -> void:
	_target = null; _use_position = false
	target_lost.emit()


func has_target() -> bool:
	return (_target and is_instance_valid(_target)) or _use_position


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
