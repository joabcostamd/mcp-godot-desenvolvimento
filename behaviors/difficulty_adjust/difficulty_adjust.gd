@tool class_name DifficultyAdjust extends Node
signal difficulty_changed(level:String)
var _init:=false
func _ready()->void:if _init:return;_init=true
func adjust(l:String)->void:difficulty_changed.emit(l)
func _get_configuration_warnings()->PackedStringArray:return[]