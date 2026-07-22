## Behavior animation_blender para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: animation_blender
@tool class_name AnimationBlender extends Node
signal animation_player_changed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func set_player(p:String)->void:animation_player_changed.emit()
func _get_configuration_warnings()->PackedStringArray:return[]