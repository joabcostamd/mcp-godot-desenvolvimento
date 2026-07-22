## Behavior physics_tick_optimizer para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: physics_tick_optimizer
@tool class_name PhysicsTickOptimizer extends Node
signal tick_rate_changed(rate:float)
var _init:=false
func _ready()->void:if _init:return;_init=true
@export var rate:float=60.0:set(v)=rate=v;tick_rate_changed.emit(v)
func _get_configuration_warnings()->PackedStringArray:return[]