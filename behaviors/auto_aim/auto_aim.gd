@tool class_name AutoAim extends Node
signal aim_adjusted()
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]