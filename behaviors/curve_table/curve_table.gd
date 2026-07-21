## Behavior curve_table para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: curve_table
@tool class_name CurveTable extends Resource
signal curve_updated()
var _init:=false
func _ready()->void:if _init:return;_init=true
func update_curve()->void:curve_updated.emit()
func _get_configuration_warnings()->PackedStringArray:return[]