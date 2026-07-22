## CameraZoom — Zoom de Câmera | Godot 4.7 Style Guide compliant.
##
## Aplica zoom suave na Camera2D via Tween.
## zoom_to(target, duration) com cancelamento de transição anterior.
## Sem câmera = no-op seguro. Detecta parent Camera2D ou viewport.
##
## @behavior: camera_zoom
## @genres: generic
## @tutorial: behaviors/camera_zoom/README.md

@tool
class_name CameraZoom
extends Node

@export var default_zoom: Vector2 = Vector2(1.0, 1.0)
@export var default_duration: float = 0.5: set(v): default_duration = clampf(v, 0, 5)

signal zoom_started(target: Vector2)
signal zoom_finished(current: Vector2)

var _tween: Tween = null
var _camera: Camera2D = null
var _active: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_camera()
	_initialized = true


func _find_camera() -> void:
	# Tenta parent como Camera2D
	var p := get_parent()
	if p is Camera2D:
		_camera = p as Camera2D
		return

	# Tenta viewport
	var vp := get_viewport()
	if vp:
		_camera = vp.get_camera_2d()


## Aplica zoom para o alvo. duration < 0 usa default_duration.
## Sem câmera = no-op.
func zoom_to(target: Vector2, duration: float = -1.0) -> void:
	if not _camera:
		_find_camera()
	if not _camera:
		return

	var dur := default_duration if duration < 0 else duration
	dur = maxf(dur, 0.0)

	_kill_tween()

	if dur <= 0.0:
		_camera.zoom = target
		zoom_started.emit(target)
		zoom_finished.emit(target)
		return

	_active = true
	zoom_started.emit(target)

	var current := _camera.zoom
	_tween = create_tween()
	_tween.tween_property(_camera, "zoom", target, dur)
	_tween.tween_callback(_on_zoom_done)


func _on_zoom_done() -> void:
	_tween = null
	_active = false
	if _camera:
		zoom_finished.emit(_camera.zoom)


## Restaura o zoom para default_zoom.
func reset(duration: float = -1.0) -> void:
	zoom_to(default_zoom, duration)


## Retorna o zoom atual da câmera, ou Vector2.ONE se sem câmera.
func get_current_zoom() -> Vector2:
	if _camera:
		return _camera.zoom
	return Vector2.ONE


func _kill_tween() -> void:
	if _tween and is_instance_valid(_tween):
		_tween.kill()
	_tween = null


func is_active() -> bool:
	return _active


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
