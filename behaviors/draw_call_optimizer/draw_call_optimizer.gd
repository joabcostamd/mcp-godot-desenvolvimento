## Behavior draw_call_optimizer para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: draw_call_optimizer
@tool class_name DrawCallOptimizer extends Node
signal optimized()
var _init:=false
func _ready()->void:if _init:return;_init=true
func optimize()->void:optimized.emit()
func _get_configuration_warnings()->PackedStringArray:return[]