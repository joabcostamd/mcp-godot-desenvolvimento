## Behavior interface_resize para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: interface_resize
@tool class_name InterfaceResize extends Control
signal resized()
var _init:=false
func _ready()->void:if _init:return;_init=true
func resize()->void:resized.emit()
func _get_configuration_warnings()->PackedStringArray:return[]