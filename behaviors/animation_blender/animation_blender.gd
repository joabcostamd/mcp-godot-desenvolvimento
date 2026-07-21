@tool class_name AnimationBlender extends Node
signal animation_player_changed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func set_player(p:String)->void:animation_player_changed.emit()
func _get_configuration_warnings()->PackedStringArray:return[]