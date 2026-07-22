## Behavior one_shot_animation para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: one_shot_animation
@tool class_name OneShotAnimation extends Node
signal shot_played();signal shot_finished()
var _init:=false
func _ready()->void:if _init:return;_init=true
func play()->void:shot_played.emit()
func finish()->void:shot_finished.emit()
func _get_configuration_warnings()->PackedStringArray:return[]