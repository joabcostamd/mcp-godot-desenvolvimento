## TimerBehavior — Timer Wrapper | Godot 4.7 Style Guide compliant.
##
## Node + Timer child com start/stop/restart/pause/resume.
## Emite timeout e tick. one_shot e auto_start configuráveis.
##
## @behavior: timer
## @genres: generic
## @tutorial: behaviors/timer/README.md

@tool
class_name TimerBehavior
extends Node

@export var wait_time: float = 1.0: set(v): wait_time = clampf(v, 0.01, 3600)
@export var one_shot: bool = false
@export var auto_start: bool = false

signal timeout()
signal tick()

var _timer: Timer = null
var _initialized: bool = false
var _paused: bool = false
var _remaining: float = 0.0


func _ready() -> void:
	if _initialized: return
	_setup_timer()
	_initialized = true
	if auto_start: start()


func _setup_timer() -> void:
	_timer = Timer.new()
	_timer.name = "TimerInternal"
	_timer.one_shot = one_shot
	_timer.wait_time = wait_time
	_timer.timeout.connect(_on_timeout)
	add_child(_timer)


func _on_timeout() -> void:
	tick.emit()
	if one_shot:
		timeout.emit()
	else:
		timeout.emit()


func start() -> void:
	if not _timer: _setup_timer()
	_timer.wait_time = wait_time
	_timer.one_shot = one_shot
	_paused = false
	_timer.start()


func stop() -> void:
	if _timer: _timer.stop()
	_paused = false


func restart() -> void:
	stop()
	start()


func pause() -> void:
	if _timer and not _timer.is_stopped():
		_remaining = _timer.time_left
		_timer.stop()
		_paused = true


func resume() -> void:
	if _paused and _timer:
		_timer.wait_time = _remaining
		_timer.start()
		_paused = false


func is_running() -> bool:
	return _timer != null and not _timer.is_stopped()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
