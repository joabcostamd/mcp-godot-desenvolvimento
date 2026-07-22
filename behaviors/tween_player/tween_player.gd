## TweenPlayer — Player de Tween Genérico | Godot 4.7 Style Guide compliant.
##
## Anima qualquer propriedade de qualquer nó com easing/delay configuráveis.
## play(node, property, target, duration). Suporta cancelamento.
##
## @behavior: tween_player
## @genres: generic
## @tutorial: behaviors/tween_player/README.md

@tool
class_name TweenPlayer
extends Node

@export var default_duration: float = 0.5: set(v): default_duration = clampf(v, 0.01, 10)
@export var default_easing: int = 1: set(v): default_easing = clampi(v, 0, 3)
@export var default_transition: int = 2: set(v): default_transition = clampi(v, 0, 5)
@export var default_delay: float = 0.0: set(v): default_delay = clampf(v, 0, 5)

signal tween_started(property: String)
signal tween_finished(property: String)

var _tween: Tween = null


## Anima uma propriedade de um nó.
## duration < 0 usa default_duration.
## easing/transition < 0 usam defaults.
func play(node: Node, prop: StringName, target: Variant, duration: float = -1.0, delay: float = -1.0, easing: int = -1, transition: int = -1) -> void:
	if not is_instance_valid(node):
		return

	var dur := default_duration if duration < 0 else duration
	var dly := default_delay if delay < 0 else delay
	var es := default_easing if easing < 0 else easing
	var tr := default_transition if transition < 0 else transition

	dur = maxf(dur, 0.01)
	dly = maxf(dly, 0.0)

	stop()

	_tween = create_tween()
	var tw := _tween.tween_property(node, prop, target, dur)

	if dly > 0:
		tw.set_delay(dly)

	tw.set_ease(es)
	tw.set_trans(tr)

	tween_started.emit(prop)

	_tween.tween_callback(_on_finished.bind(prop))


func _on_finished(prop: StringName) -> void:
	_tween = null
	tween_finished.emit(prop)


## Cancela o tween atual.
func stop() -> void:
	if _tween and is_instance_valid(_tween):
		_tween.kill()
	_tween = null


func is_playing() -> bool:
	return _tween != null and is_instance_valid(_tween)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
