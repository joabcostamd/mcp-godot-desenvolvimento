## Behavior bypass_gate para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: bypass_gate
@tool class_name BypassGate extends Node
signal gate_bypassed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func bypass()->void:gate_bypassed.emit()
func _get_configuration_warnings()->PackedStringArray:return[]