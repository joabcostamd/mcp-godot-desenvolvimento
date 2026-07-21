## Behavior server_physics para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: server_physics
@tool class_name ServerPhysics extends Node
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]