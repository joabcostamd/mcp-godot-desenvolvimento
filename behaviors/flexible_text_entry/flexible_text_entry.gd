## Behavior flexible_text_entry para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: flexible_text_entry
@tool class_name FlexibleTextEntry extends Control
signal text_submitted(text:String)
var _init:=false
func _ready()->void:if _init:return;_init=true
func submit(t:String)->void:text_submitted.emit(t)
func _get_configuration_warnings()->PackedStringArray:return[]