## Glitch — Efeito Glitch | Godot 4.7 Style Guide compliant.
##
## Aplica deslocamento horizontal aleatório + flicker no parent Node2D.
## trigger(intensity, duration) com Tween rápido. Restaura original.
##
## @behavior: glitch
## @genres: generic
## @tutorial: behaviors/glitch/README.md

@tool
class_name Glitch
extends Node

@export var default_intensity: float = 0.5: set(v): default_intensity = clampf(v, 0, 1)
@export var default_duration: float = 0.3: set(v): default_duration = clampf(v, 0.05, 3)
@export var max_offset: float = 10.0: set(v): max_offset = clampf(v, 1, 100)
@export var flicker_speed: float = 20.0: set(v): flicker_speed = clampf(v, 5, 60)

signal glitch_started()
signal glitch_finished()

var _active: bool = false
var _original_position: Vector2 = Vector2.ZERO
var _original_modulate: Color = Color.WHITE
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	var parent := get_parent()
	if parent and parent is Node2D:
		_original_position = (parent as Node2D).position
	if parent and parent is CanvasItem:
		_original_modulate = (parent as CanvasItem).modulate
	_initialized = true


func trigger(intensity_override: float = -1.0, duration_override: float = -1.0) -> void:
	if _active:
		return

	var intensity := default_intensity if intensity_override < 0 else intensity_override
	intensity = clampf(intensity, 0, 1)
	var dur := default_duration if duration_override < 0 else duration_override
	dur = maxf(dur, 0.05)

	var parent := get_parent()
	if not parent or not parent is Node2D:
		return

	_active = true
	glitch_started.emit()

	var steps := int(dur * flicker_speed)
	if steps < 1: steps = 1
	var step_dur := dur / steps

	var tween := create_tween()
	for i in range(steps):
		var offset_x := randf_range(-max_offset * intensity, max_offset * intensity)
		var target_pos := _original_position + Vector2(offset_x, 0)
		tween.tween_property(parent, "position", target_pos, step_dur * 0.3)
		tween.tween_property(parent, "position", _original_position, step_dur * 0.7)

	tween.tween_callback(_on_finished)


func _on_finished() -> void:
	_active = false
	var parent := get_parent()
	if parent and parent is Node2D:
		(parent as Node2D).position = _original_position
	if parent and parent is CanvasItem:
		(parent as CanvasItem).modulate = _original_modulate
	glitch_finished.emit()


func is_active() -> bool:
	return _active


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
