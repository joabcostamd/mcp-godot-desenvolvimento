## Behavior blood_gore_toggle para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: blood_gore_toggle
@tool class_name BloodGoreToggle extends Node
signal toggled()
var _init:=false;@export var enabled:bool=true
func _ready()->void:if _init:return;_init=true
func toggle()->void:enabled=!enabled;toggled.emit()
func _get_configuration_warnings()->PackedStringArray:return[]