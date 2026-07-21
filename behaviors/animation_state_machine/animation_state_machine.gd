## Behavior animation_state_machine para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: animation_state_machine
@tool class_name AnimationStateMachine extends Node
signal state_changed(state:String)
var _init:=false
func _ready()->void:if _init:return;_init=true
func set_state(s:String)->void:state_changed.emit(s)
func _get_configuration_warnings()->PackedStringArray:return[]