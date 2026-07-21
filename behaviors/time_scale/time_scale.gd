## TimeScale — Controle Global de Tempo | Godot 4.7 Style Guide compliant.
##
## Manipula Engine.time_scale com transições suaves via Tween.
## set_scale(target, duration) para bullet-time/slow-motion.
## Restaura 1.0 em tree_exiting. Apenas um por cena.
##
## @behavior: time_scale
## @genres: generic
## @tutorial: behaviors/time_scale/README.md

@tool
class_name TimeScale
extends Node

@export var default_scale: float = 1.0: set(v): default_scale = clampf(v, 0.1, 10)
@export var transition_duration: float = 0.3: set(v): transition_duration = clampf(v, 0, 5)
@export var min_scale: float = 0.05: set(v): min_scale = clampf(v, 0.01, 0.5)
@export var max_scale: float = 10.0: set(v): max_scale = clampf(v, 1, 100)

signal scale_changed(new_scale: float)

var _tween: Tween = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_initialized = true


func _exit_tree() -> void:
	_kill_tween()
	Engine.time_scale = 1.0


## Define a escala de tempo alvo com transição suave.
## duration < 0 usa transition_duration.
## target <= 0 restaura default_scale.
func set_scale(target: float, duration: float = -1.0) -> void:
	var dur := transition_duration if duration < 0 else duration
	dur = maxf(dur, 0.0)

	# Valida target
	var tgt := target
	if tgt <= 0.0:
		tgt = default_scale
	else:
		tgt = clampf(tgt, min_scale, max_scale)

	_kill_tween()

	if dur <= 0.0:
		# Instantâneo
		Engine.time_scale = tgt
		scale_changed.emit(tgt)
		return

	var current := Engine.time_scale
	_tween = create_tween()
	_tween.tween_method(_apply_scale, current, tgt, dur)
	_tween.tween_callback(_on_transition_done.bind(tgt))


func _apply_scale(value: float) -> void:
	Engine.time_scale = value


func _on_transition_done(final_scale: float) -> void:
	_tween = null
	Engine.time_scale = final_scale
	scale_changed.emit(final_scale)


## Restaura a escala para default_scale.
func reset(duration: float = -1.0) -> void:
	set_scale(default_scale, duration)


## Retorna a escala atual.
func get_current_scale() -> float:
	return Engine.time_scale


func _kill_tween() -> void:
	if _tween and is_instance_valid(_tween):
		_tween.kill()
	_tween = null


func is_transitioning() -> bool:
	return _tween != null and is_instance_valid(_tween)
