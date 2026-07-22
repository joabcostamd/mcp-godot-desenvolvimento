## LerpSmooth — Interpolação Suave | Godot 4.7.
##
## Node wrapper sobre Tween para transições em uma linha.
## Suporta posição, rotação, escala, modulate.
##
## @behavior: lerp_smooth

@tool
class_name LerpSmooth
extends Node

@export var duration: float = 0.5: set(v): duration = clampf(v, 0.01, 10)
@export var easing: int = 3: set(v): easing = clampi(v, 0, 3)

signal completed()

var _tween: Tween
var _initialized: bool = false

const EASE_TYPES := [Tween.EASE_IN, Tween.EASE_OUT, Tween.EASE_IN_OUT]


func _ready() -> void:
	if _initialized: return
	_initialized = true


func _get_ease_type() -> int:
	if easing == 0: return 0  # linear (no ease)
	if easing >= 1 and easing <= 3: return EASE_TYPES[easing - 1]
	return Tween.EASE_IN_OUT


func _get_trans_type() -> int:
	return Tween.TRANS_QUAD


func move_to(target: Vector2) -> void:
	var p := get_parent()
	if not p is Node2D: return
	_kill_tween()
	_tween = create_tween()
	_tween.tween_property(p, "position", target, duration).set_trans(_get_trans_type()).set_ease(_get_ease_type())
	_tween.tween_callback(func(): completed.emit())


func rotate_to(target: float) -> void:
	var p := get_parent()
	if not p is Node2D: return
	_kill_tween()
	_tween = create_tween()
	_tween.tween_property(p, "rotation", target, duration).set_trans(_get_trans_type()).set_ease(_get_ease_type())
	_tween.tween_callback(func(): completed.emit())


func scale_to(target: Vector2) -> void:
	var p := get_parent()
	if not p is Node2D: return
	_kill_tween()
	_tween = create_tween()
	_tween.tween_property(p, "scale", target, duration).set_trans(_get_trans_type()).set_ease(_get_ease_type())
	_tween.tween_callback(func(): completed.emit())


func modulate_to(target: Color) -> void:
	var p := get_parent()
	if not p is CanvasItem: return
	_kill_tween()
	_tween = create_tween()
	_tween.tween_property(p, "modulate", target, duration).set_trans(_get_trans_type()).set_ease(_get_ease_type())
	_tween.tween_callback(func(): completed.emit())


func _kill_tween() -> void:
	if _tween and _tween.is_valid(): _tween.kill()
	_tween = null


func stop() -> void: _kill_tween()
func is_running() -> bool: return _tween != null and _tween.is_valid()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
