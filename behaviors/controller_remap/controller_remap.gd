## Behavior Controller Remap para Godot 4.
## Generos: generic.
## Tags: acessibilidade.
## Extends: Node.
## Sinais: rebound().
## Dependencias: nenhuma.
## @behavior: controller_remap
@tool class_name ControllerRemap extends Control
@export var actions: Array = []
signal rebound(action: String)
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func rebind(action: String, event: InputEvent) -> void:
	if not InputMap.has_action(action): return
	InputMap.action_add_event(action,event); rebound.emit(action)
func _get_configuration_warnings() -> PackedStringArray: return []
