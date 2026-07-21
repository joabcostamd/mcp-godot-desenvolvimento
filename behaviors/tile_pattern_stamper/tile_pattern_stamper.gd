@tool class_name TilePatternStamper extends Node
signal pattern_stamped();signal pattern_saved()
var _init:=false
func _ready()->void:if _init:return;_init=true
func stamp()->void:pattern_stamped.emit()
func _get_configuration_warnings()->PackedStringArray:return[]