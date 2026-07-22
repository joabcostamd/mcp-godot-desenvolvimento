## Behavior stereo_to_mono para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: stereo_to_mono
@tool class_name StereoToMono extends Node
var _init:=false;@export var enabled:bool=true
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]