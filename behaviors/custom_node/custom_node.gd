## Behavior custom_node para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: custom_node
@tool class_name CustomNode extends Node; signal node_registered(class_name: String); signal node_unregistered(class_name: String)
var _initialized: bool = false; func _ready() -> void: if _initialized: return; _initialized=true
func register(class_name: String) -> void: node_registered.emit(class_name)
func unregister(class_name: String) -> void: node_unregistered.emit(class_name)
func _get_configuration_warnings() -> PackedStringArray: return []