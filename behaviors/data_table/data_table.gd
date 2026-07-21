## Behavior data_table para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: data_table
@tool class_name DataTable extends Resource
signal data_changed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func notify_change()->void:data_changed.emit()
func _get_configuration_warnings()->PackedStringArray:return[]