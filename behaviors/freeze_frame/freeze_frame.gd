## FreezeFrame — Congelamento Total | Godot 4.7 Style Guide compliant.
##
## Congela o jogo completamente (Engine.time_scale = 0) por uma duração.
## Timer com ignore_time_scale=true garante contagem mesmo parado.
## freeze(duration) inicia. Ignora chamadas durante freeze ativo.
##
## @behavior: freeze_frame
## @genres: generic
## @tutorial: behaviors/freeze_frame/README.md

@tool
class_name FreezeFrame
extends Node

@export var default_duration: float = 0.3: set(v): default_duration = clampf(v, 0.01, 5)
@export var restore_duration: float = 0.1: set(v): restore_duration = clampf(v, 0, 2)

signal frozen()
signal resumed()

var _timer: Timer = null
var _tween: Tween = null
var _active: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_setup_timer()
	_initialized = true


func _setup_timer() -> void:
	_timer = Timer.new()
	_timer.name = "FreezeFrameTimer"
	_timer.one_shot = true
	_timer.ignore_time_scale = true  # Essencial: contar mesmo com time_scale=0
	_timer.timeout.connect(_on_timer_timeout)
	add_child(_timer)


func _exit_tree() -> void:
	_kill_tween()
	if _timer:
		_timer.stop()
	Engine.time_scale = 1.0


## Congela o jogo completamente.
## duration_override < 0 usa default_duration.
func freeze(duration_override: float = -1.0) -> void:
	if _active:
		return

	if not _timer:
		_setup_timer()

	var dur := default_duration if duration_override < 0 else duration_override
	dur = maxf(dur, 0.01)

	_active = true
	Engine.time_scale = 0.0
	_timer.start(dur)
	frozen.emit()


func _on_timer_timeout() -> void:
	if restore_duration <= 0.0:
		_restore_instant()
		return

	_kill_tween()
	var current := Engine.time_scale
	_tween = create_tween()
	_tween.tween_method(_apply_scale, current, 1.0, restore_duration)
	_tween.tween_callback(_on_restore_done)


func _apply_scale(value: float) -> void:
	Engine.time_scale = value


func _restore_instant() -> void:
	Engine.time_scale = 1.0
	_on_restore_done()


func _on_restore_done() -> void:
	_tween = null
	_active = false
	Engine.time_scale = 1.0
	resumed.emit()


func _kill_tween() -> void:
	if _tween and is_instance_valid(_tween):
		_tween.kill()
	_tween = null


func is_active() -> bool:
	return _active
