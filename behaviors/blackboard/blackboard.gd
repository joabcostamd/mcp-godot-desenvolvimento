## Node que funciona como quadro de variáveis compartilhadas.
## Generos: generic.
## Tags: dados, contexto.
## Extends: Node.
## Sinais: var_set(), trigger_activated().
## Dependencias: nenhuma.
## @behavior: blackboard
@tool
class_name Blackboard
extends Node
signal var_set(key: String)
signal trigger_activated(key: String)
var _vars: Dictionary = {}
var _triggers: Dictionary = {}

func set_var(key: String, value) -> void:
	var old = _vars.get(key); _vars[key]=value
	if old != value: var_set.emit(key)
	if _triggers.has(key): trigger_activated.emit(key); (_triggers[key] as Callable).call(value)

func get_var(key: String, default = null):
	return _vars.get(key, default)

func has_var(key: String) -> bool: return _vars.has(key)
func erase_var(key: String) -> void: _vars.erase(key)
func set_trigger(key: String, callback: Callable) -> void: _triggers[key]=callback
func clear() -> void: _vars.clear(); _triggers.clear()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
