## ChromaticAberration — Aberração Cromática Simulada | Godot 4.7.
##
## Simula chromatic aberration via flicker RGB no modulate do parent.
## trigger(intensity, duration) oscila entre canais e restaura.
##
## @behavior: chromatic_aberration
## @genres: generic
## @tutorial: behaviors/chromatic_aberration/README.md

@tool
class_name ChromaticAberration
extends Node

@export var default_intensity: float = 0.5: set(v): default_intensity = clampf(v, 0, 1)
@export var default_duration: float = 0.3: set(v): default_duration = clampf(v, 0.05, 3)
@export var flicker_speed: float = 20.0: set(v): flicker_speed = clampf(v, 5, 60)

signal aberration_started()
signal aberration_finished()

var _active: bool = false
var _original_modulate: Color = Color.WHITE
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	var parent := get_parent()
	if parent and parent is CanvasItem:
		_original_modulate = (parent as CanvasItem).modulate
	_initialized = true


## Dispara o efeito. intensity_override < 0 usa default_intensity.
func trigger(intensity_override: float = -1.0, duration_override: float = -1.0) -> void:
	if _active:
		return

	var intensity := default_intensity if intensity_override < 0 else intensity_override
	var duration := default_duration if duration_override < 0 else duration_override
	intensity = clampf(intensity, 0, 1)
	duration = maxf(duration, 0.05)

	var parent := get_parent()
	if not parent or not parent is CanvasItem:
		return

	_active = true
	aberration_started.emit()

	# Cria Tween com múltiplos flickers RGB
	var tween := create_tween()
	var steps := int(duration * flicker_speed)
	if steps < 1: steps = 1

	var step_dur := duration / steps
	var colors := [
		Color.RED.lerp(_original_modulate, 1.0 - intensity),
		Color.GREEN.lerp(_original_modulate, 1.0 - intensity),
		Color.BLUE.lerp(_original_modulate, 1.0 - intensity),
	]

	for i in range(steps):
		var c := colors[i % 3]
		tween.tween_property(parent, "modulate", c, step_dur * 0.5)
		tween.tween_property(parent, "modulate", _original_modulate, step_dur * 0.5)

	tween.tween_callback(_on_finished)


func _on_finished() -> void:
	_active = false
	var parent := get_parent()
	if parent and parent is CanvasItem:
		(parent as CanvasItem).modulate = _original_modulate
	aberration_finished.emit()


func is_active() -> bool:
	return _active
