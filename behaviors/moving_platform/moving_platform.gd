## MovingPlatform — Plataforma Móvel | Godot 4.7.
##
## AnimatableBody2D que segue um Path2D filho.
## Velocidade configurável, loop e pausa nas pontas.
##
## @behavior: moving_platform
## @genres: platformer, puzzle, generic
## @tutorial: behaviors/moving_platform/README.md

@tool
class_name MovingPlatform
extends AnimatableBody2D

## Velocidade ao longo do path (px/s).
@export var speed: float = 100.0:
	set(v):
		speed = clampf(v, 10.0, 2000.0)

## Reinicia ao chegar ao fim.
@export var loop: bool = true

## Tempo de pausa nas pontas (s).
@export var pause_at_ends: float = 0.0:
	set(v):
		pause_at_ends = clampf(v, 0.0, 10.0)
		if _pause_timer:
			_pause_timer.wait_time = pause_at_ends

signal waypoint_reached(index: int)
signal loop_completed()

var _path: Path2D
var _progress: float = 0.0
var _direction: int = 1  # 1 = forward, -1 = backward
var _paused: bool = false
var _pause_timer: Timer
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_path()
	_create_timer()
	_initialized = true


func _find_path() -> void:
	for child in get_children():
		if child is Path2D:
			_path = child as Path2D
			break


func _create_timer() -> void:
	if _pause_timer:
		return
	_pause_timer = Timer.new()
	_pause_timer.name = "PauseTimer"
	_pause_timer.one_shot = true
	_pause_timer.wait_time = pause_at_ends
	_pause_timer.timeout.connect(_resume)
	add_child(_pause_timer)


func _physics_process(delta: float) -> void:
	if _paused or not _path:
		return

	var curve := _path.curve
	if not curve or curve.point_count < 2:
		return

	var total_length := _get_curve_length(curve)

	# Avança
	_progress += speed * delta * _direction

	# Verifica pontas
	if _progress >= total_length:
		_progress = total_length
		waypoint_reached.emit(1)  # fim
		if loop:
			loop_completed.emit()
			if pause_at_ends > 0.0 and _pause_timer:
				_paused = true
				_pause_timer.start()
		else:
			_direction = -1
			if pause_at_ends > 0.0 and _pause_timer:
				_paused = true
				_pause_timer.start()

	elif _progress <= 0.0:
		_progress = 0.0
		waypoint_reached.emit(0)  # início
		if loop:
			if pause_at_ends > 0.0 and _pause_timer:
				_paused = true
				_pause_timer.start()
		else:
			_direction = 1
			if pause_at_ends > 0.0 and _pause_timer:
				_paused = true
				_pause_timer.start()

	# Atualiza posição
	global_position = curve.sample_baked(_progress, true)


func _resume() -> void:
	_paused = false
	if loop:
		_progress = 0.0 if _progress >= _get_curve_length(_path.curve) else _progress
	else:
		_direction *= -1


func _get_curve_length(curve: Curve2D) -> float:
	return curve.get_baked_length() if curve.get_baked_length() > 0.0 else 1.0


## Reinicia do início do path.
func reset_position() -> void:
	_progress = 0.0
	_direction = 1
	_paused = false


## Retorna o progresso atual (0.0 a 1.0).
func get_progress_ratio() -> float:
	if not _path or not _path.curve:
		return 0.0
	var length := _get_curve_length(_path.curve)
	return _progress / length if length > 0.0 else 0.0
