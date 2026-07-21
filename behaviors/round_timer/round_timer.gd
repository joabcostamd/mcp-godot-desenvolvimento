## RoundTimer — Timer de Rodada | Godot 4.7 Style Guide compliant.
##
## Node + Timer para contagem regressiva/progressiva com sinais de round.
## countdown decrementa; pause_on_end pausa ao terminar.
##
## @behavior: round_timer
## @genres: survivor_like, tower_defense, generic
## @tutorial: behaviors/round_timer/README.md

@tool
class_name RoundTimer
extends Node

@export var duration: float = 60.0: set(v): duration = clampf(v, 1, 3600)
@export var countdown: bool = true
@export var pause_on_end: bool = false

signal tick(remaining: float)
signal round_started()
signal round_ended()
signal time_up()

var _elapsed: float = 0.0
var _active: bool = false
var _tick_timer: Timer = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_setup_timer()
	_initialized = true


func _setup_timer() -> void:
	_tick_timer = Timer.new()
	_tick_timer.name = "TickTimer"
	_tick_timer.one_shot = false
	_tick_timer.wait_time = 1.0
	_tick_timer.timeout.connect(_on_tick)
	add_child(_tick_timer)


func start() -> void:
	_elapsed = 0.0
	_active = true
	if _tick_timer: _tick_timer.start()
	round_started.emit()


func _on_tick() -> void:
	if not _active: return
	_elapsed += 1.0
	var remaining := duration - _elapsed if countdown else _elapsed
	tick.emit(maxf(remaining, 0))

	if countdown and _elapsed >= duration:
		_time_up()


func _time_up() -> void:
	time_up.emit()
	_finish()


func stop() -> void:
	_finish()


func _finish() -> void:
	_active = false
	if _tick_timer: _tick_timer.stop()
	round_ended.emit()
	if pause_on_end:
		get_tree().paused = true


func get_remaining() -> float:
	if countdown:
		return maxf(duration - _elapsed, 0)
	return _elapsed


func is_active() -> bool:
	return _active
