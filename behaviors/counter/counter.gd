## Counter — Contador | Godot 4.7.
##
## Node com valor mínimo/máximo e step configurável.
## increment/decrement com clamp. Sinais em mudança e limites.
##
## @behavior: counter
## @genres: generic
## @tutorial: behaviors/counter/README.md

@tool
class_name Counter
extends Node

@export var initial_value: int = 0
@export var min_value: int = 0
@export var max_value: int = 0
@export var step: int = 1:
	set(v): step = clampi(v, 1, 1000)

signal value_changed(new_value: int, old_value: int)
signal min_reached()
signal max_reached()

var _value: int = 0
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_value = clampi(initial_value, min_value, max_value if max_value > 0 else 999999)
	_initialized = true


func increment() -> int:
	return add(step)


func decrement() -> int:
	return add(-step)


func add(amount: int) -> int:
	var old := _value
	_value += amount
	if max_value > 0 and _value > max_value:
		_value = max_value
	if _value < min_value:
		_value = min_value

	if _value != old:
		value_changed.emit(_value, old)

	if _value == min_value and old != min_value:
		min_reached.emit()
	if max_value > 0 and _value == max_value and old != max_value:
		max_reached.emit()

	return _value


func set_value(v: int) -> void:
	var old := _value
	_value = clampi(v, min_value, max_value if max_value > 0 else 999999)
	if _value != old:
		value_changed.emit(_value, old)


func get_value() -> int:
	return _value


func reset() -> void:
	set_value(initial_value)


func is_at_min() -> bool:
	return _value == min_value


func is_at_max() -> bool:
	return max_value > 0 and _value == max_value


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if min_value > initial_value:
		w.append("min_value is greater than initial_value — counter starts below minimum.")
	if max_value > 0 and max_value < min_value:
		w.append("max_value is less than min_value — no valid range.")
	return w
