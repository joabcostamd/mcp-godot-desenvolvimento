@tool class_name PhysicsTickOptimizer extends Node
signal tick_rate_changed(rate:float)
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]