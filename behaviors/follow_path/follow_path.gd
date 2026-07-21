## FollowPath — Seguir Caminho | Godot 4.7.
##
## Node que move o parent Node2D ao longo de um Path2D filho.
##
## @behavior: follow_path

@tool
class_name FollowPath
extends Node

@export var speed: float = 100.0: set(v): speed = clampf(v, 10, 2000)
@export var loop: bool = true
@export var look_along: bool = false

signal path_finished()

var _path: Path2D
var _progress: float = 0.0
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	for c in get_children():
		if c is Path2D: _path = c; break
	_initialized = true


func _physics_process(delta: float) -> void:
	var parent := get_parent()
	if not _path or not parent is Node2D: return
	var curve := _path.curve
	if not curve or curve.point_count < 2: return

	var length := curve.get_baked_length()
	if length <= 0: return

	_progress += speed * delta
	if _progress >= length:
		if loop:
			_progress = fmod(_progress, length)
			path_finished.emit()
		else:
			_progress = length; return

	var p := parent as Node2D
	p.global_position = curve.sample_baked(_progress, true)
	if look_along and _progress + 1.0 < length:
		var next := curve.sample_baked(_progress + 1.0, true)
		p.rotation = p.global_position.direction_to(next).angle()


func reset() -> void: _progress = 0.0
func get_progress() -> float: return _progress
