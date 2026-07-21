@tool
class_name Recoil
extends Node

@export var recoil_amount: float = 20.0: set(v): recoil_amount=clampf(v,1,200)
@export var recovery_speed: float = 100.0: set(v): recovery_speed=clampf(v,1,500)
@export var recoil_direction: Vector2 = Vector2(-1,0): set(v): recoil_direction=v.normalized() if v.length()>0 else Vector2(-1,0)

var _offset: Vector2 = Vector2.ZERO
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_initialized = true

func _process(delta: float) -> void:
	var p := get_parent(); if not p is Node2D: return
	_offset = _offset.move_toward(Vector2.ZERO, recovery_speed * delta)
	(p as Node2D).position += _offset

func apply_recoil() -> void:
	_offset += recoil_direction * recoil_amount

func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not get_parent() is Node2D: w.append("Parent must be Node2D for position offset to work.")
	return w
