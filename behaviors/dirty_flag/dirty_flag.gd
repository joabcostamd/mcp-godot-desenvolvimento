@tool class_name DirtyFlag extends Node
signal dirty();signal clean()
var _init:=false
func _ready()->void:if _init:return;_init=true
func mark_dirty()->void:dirty.emit()
func mark_clean()->void:clean.emit()
func _get_configuration_warnings()->PackedStringArray:return[]