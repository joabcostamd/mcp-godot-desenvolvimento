@tool class_name SkeletonIk extends Node
signal ik_solved()
var _init:=false
func _ready()->void:if _init:return;_init=true
func solve()->void:ik_solved.emit()
func _get_configuration_warnings()->PackedStringArray:return[]