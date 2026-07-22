## CameraFollow — Camera Segue Alvo | Godot 4.7.
##
## Node que faz a Camera2D parent seguir um alvo Node2D.
## Suporte a offset, damping por eixo, look_ahead e limites.
##
## @behavior: camera_follow
## @genres: platformer, topdown_shooter, metroidvania, generic
## @tutorial: behaviors/camera_follow/README.md

@tool
class_name CameraFollow
extends Node

@export var target: NodePath = NodePath()
@export var offset: Vector2 = Vector2.ZERO
@export var damping: float = 0.1:
	set(v):
		damping = clampf(v, 0.0, 1.0)
@export var look_ahead: float = 0.0:
	set(v):
		look_ahead = clampf(v, 0.0, 200.0)

var _target_node: Node2D = null
var _last_target_pos: Vector2 = Vector2.ZERO
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_resolve_target()
	_initialized = true


func _resolve_target() -> void:
	if target.is_empty():
		var parent := get_parent()
		if parent is Node2D:
			_target_node = parent as Node2D
	else:
		_target_node = get_node(target) as Node2D

	if _target_node:
		_last_target_pos = _target_node.global_position


func _process(_delta: float) -> void:
	if not _target_node or not is_instance_valid(_target_node):
		return

	var camera := _get_camera()
	if not camera:
		return

	# Posicao desejada
	var target_pos := _target_node.global_position + offset

	# Look ahead: antecipa na direcao do movimento
	if look_ahead > 0.0:
		var velocity := _target_node.global_position - _last_target_pos
		target_pos += velocity.normalized() * look_ahead if velocity.length() > 0.01 else Vector2.ZERO

	# Suavizacao
	if damping <= 0.0:
		camera.global_position = target_pos
	else:
		camera.global_position = camera.global_position.lerp(target_pos, 1.0 - damping)

	_last_target_pos = _target_node.global_position


func _get_camera() -> Camera2D:
	var parent := get_parent()
	if parent is Camera2D:
		return parent as Camera2D

	# Busca Camera2D no parent ou acima
	var p: Node = get_parent()
	while p:
		if p is Camera2D:
			return p as Camera2D
		p = p.get_parent()

	return null


## Define o alvo programaticamente.
func set_target(node: Node2D) -> void:
	_target_node = node
	if node:
		_last_target_pos = node.global_position


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	var camera := _get_camera()
	if not camera:
		w.append("No Camera2D found in parent hierarchy — camera won't move.")
	if not _target_node and target.is_empty():
		w.append("No target set — use set_target() or configure the target NodePath.")
	return w
