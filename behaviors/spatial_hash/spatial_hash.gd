## Behavior spatial_hash para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: spatial_hash
@tool class_name SpatialHash extends Node
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]