@tool class_name FlexibleTextEntry extends Control
signal text_submitted(text:String)
var _init:=false
func _ready()->void:if _init:return;_init=true
func submit(t:String)->void:text_submitted.emit(t)
func _get_configuration_warnings()->PackedStringArray:return[]