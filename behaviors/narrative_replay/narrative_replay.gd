@tool class_name NarrativeReplay extends Node
signal replayed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func replay()->void:replayed.emit()
func _get_configuration_warnings()->PackedStringArray:return[]