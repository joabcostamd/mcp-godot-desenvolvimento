## Behavior root_motion_controller para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: root_motion_controller
@tool class_name RootMotionController extends Node
signal motion_applied()
var _init:=false
func _ready()->void:if _init:return;_init=true
func apply()->void:motion_applied.emit()
func _get_configuration_warnings()->PackedStringArray:return[]