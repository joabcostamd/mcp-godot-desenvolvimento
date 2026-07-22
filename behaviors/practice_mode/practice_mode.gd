## Behavior practice_mode para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: practice_mode
@tool class_name PracticeMode extends Node
signal mode_changed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func enable()->void:mode_changed.emit()
func _get_configuration_warnings()->PackedStringArray:return[]