## Behavior batch_renderer para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: batch_renderer
@tool class_name BatchRenderer extends Node
signal batch_full()
var _init:=false
func _ready()->void:if _init:return;_init=true
func notify_full()->void:batch_full.emit()
func _get_configuration_warnings()->PackedStringArray:return[]