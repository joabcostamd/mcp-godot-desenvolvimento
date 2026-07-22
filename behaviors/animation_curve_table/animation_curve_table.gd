## Behavior animation_curve_table para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: animation_curve_table
@tool class_name AnimationCurveTable extends Resource
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]