## Behavior auto_aim para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: auto_aim
@tool class_name AutoAim extends Node
signal aim_adjusted()
var _init:=false
func _ready()->void:if _init:return;_init=true
func adjust()->void:aim_adjusted.emit()
func _get_configuration_warnings()->PackedStringArray:return[]