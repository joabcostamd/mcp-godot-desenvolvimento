## EventBus — Barramento de Eventos | Godot 4.7.
@tool
class_name EventBus
extends Node

signal event_fired(event_name: String, payload: Dictionary)
var _listeners: Dictionary = {}  # event_name -> Array[Callable]

func register(event_name: String, callback: Callable) -> void:
	if not _listeners.has(event_name): _listeners[event_name]=[]
	_listeners[event_name].append(callback)

func unregister(event_name: String, callback: Callable) -> void:
	if _listeners.has(event_name): _listeners[event_name].erase(callback)

func fire(event_name: String, payload: Dictionary = {}) -> void:
	event_fired.emit(event_name, payload)
	if _listeners.has(event_name):
		for cb in _listeners[event_name]:
			if cb.is_valid(): cb.call(payload)

func clear() -> void: _listeners.clear()
func has_listeners(event_name: String) -> bool:
	return _listeners.has(event_name) and not (_listeners[event_name] as Array).is_empty()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	return w  # EventBus is a simple pub/sub — no common misconfigurations
