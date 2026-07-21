## HitStop — Congelamento de Impacto | Godot 4.7 Style Guide compliant.
##
## Reduz Engine.time_scale momentaneamente para dar peso a golpes.
## trigger(duration) inicia o freeze. Ignora chamadas durante freeze ativo.
## Restaura 1.0 ao sair da árvore.
##
## @behavior: hit_stop
## @genres: generic
## @tutorial: behaviors/hit_stop/README.md

@tool
class_name HitStop
extends Node

@export var freeze_scale: float = 0.05: set(v): freeze_scale = clampf(v, 0.01, 0.5)
@export var default_duration: float = 0.1: set(v): default_duration = clampf(v, 0.01, 2)
@export var restore_duration: float = 0.05: set(v): restore_duration = clampf(v, 0, 1)

signal hit_stopped()
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
	_timer.name = "HitStopTimer"
	_timer.one_shot = true
	_timer.timeout.connect(_on_timer_timeout)
	add_child(_timer)


func _exit_tree() -> void:
	_kill_tween()
	if _timer:
		_timer.stop()
	Engine.time_scale = 1.0


## Dispara o hit-stop. Ignora se já estiver ativo.
## duration_override < 0 usa default_duration.
func trigger(duration_override: float = -1.0) -> void:
	if _active:
		return

	if not _timer:
		_setup_timer()

	var dur := default_duration if duration_override < 0 else duration_override
	dur = maxf(dur, 0.01)

	_active = true
	Engine.time_scale = freeze_scale
	_timer.start(dur)
	hit_stopped.emit()


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
