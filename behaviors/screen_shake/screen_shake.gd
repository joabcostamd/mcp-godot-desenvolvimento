## ScreenShake — Tremor de Tela | Godot 4.7 Style Guide compliant.
##
## Aplica offset aleatório na câmera para efeito de tremor.
## trigger() dispara. Parâmetros: intensity, duration, decay.
##
## @behavior: screen_shake
## @genres: generic
## @tutorial: behaviors/screen_shake/README.md

@tool
class_name ScreenShake
extends Node

@export var intensity: float = 5.0: set(v): intensity = clampf(v, 0, 100)
@export var duration: float = 0.3: set(v): duration = clampf(v, 0.01, 5)
@export var decay: float = 0.8: set(v): decay = clampf(v, 0, 1)

signal shake_started()
signal shake_ended()

var _elapsed: float = 0.0
var _current_intensity: float = 0.0
var _original_offset: Vector2 = Vector2.ZERO
var _camera: Camera2D = null
var _active: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_find_camera()
	_initialized = true


func _find_camera() -> void:
	var p := get_parent()
	if p is Camera2D:
		_camera = p as Camera2D


## Dispara o tremor. intensity_override < 0 usa o @export intensity.
func trigger(intensity_override: float = -1.0) -> void:
	if _active: return  # não interrompe shake em andamento
	if not _camera:
		_find_camera()
	if _camera:
		_original_offset = _camera.offset
	_current_intensity = intensity_override if intensity_override >= 0 else intensity
	_elapsed = 0.0
	_active = true
	shake_started.emit()


func _process(delta: float) -> void:
	if not _active: return
	_elapsed += delta
	if _elapsed >= duration:
		_stop()
		return

	var progress := _elapsed / duration
	var current := _current_intensity * (1.0 - progress * decay)
	_apply_offset(current)


func _apply_offset(strength: float) -> void:
	var offset := Vector2(randf_range(-strength, strength), randf_range(-strength, strength))
	if _camera:
		_camera.offset = _original_offset + offset


func _stop() -> void:
	if _camera:
		_camera.offset = _original_offset
	_active = false
	shake_ended.emit()


func is_shaking() -> bool:
	return _active


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
