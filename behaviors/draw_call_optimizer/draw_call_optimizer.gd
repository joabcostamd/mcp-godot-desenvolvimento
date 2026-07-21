@tool class_name DrawCallOptimizer extends Node
signal optimized()
var _init:=false
func _ready()->void:if _init:return;_init=true
func optimize()->void:optimized.emit()
func _get_configuration_warnings()->PackedStringArray:return[]