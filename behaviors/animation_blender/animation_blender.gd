@tool class_name AnimationBlender extends Node
signal animation_player_changed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]