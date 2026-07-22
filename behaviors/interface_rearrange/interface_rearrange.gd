## Behavior interface_rearrange para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: interface_rearrange
@tool class_name InterfaceRearrange extends Control
signal rearranged();signal layout_saved()
var _init:=false
func _ready()->void:if _init:return;_init=true
func rearrange()->void:rearranged.emit()
func save_layout()->void:layout_saved.emit()
func _get_configuration_warnings()->PackedStringArray:return[]