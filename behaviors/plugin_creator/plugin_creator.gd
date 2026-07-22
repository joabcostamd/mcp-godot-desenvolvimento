## Behavior plugin_creator para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: plugin_creator
@tool class_name PluginCreator extends Node; signal plugin_created(name: String); signal plugin_built(name: String)
var _initialized: bool = false; func _ready() -> void: if _initialized: return; _initialized=true
func create(name: String) -> void: plugin_created.emit(name)
func build(name: String) -> void: plugin_built.emit(name)
func _get_configuration_warnings() -> PackedStringArray: return []