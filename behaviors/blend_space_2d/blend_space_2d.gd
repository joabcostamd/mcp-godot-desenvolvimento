## Behavior blend_space_2d para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: blend_space_2d
@tool class_name BlendSpace2d extends Node
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]