@tool class_name BatchRenderer extends Node
signal batch_full()
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]