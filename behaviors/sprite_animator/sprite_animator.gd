@tool class_name SpriteAnimator extends Node
signal animation_finished();signal animation_changed(name:String)
var _init:=false
func _ready()->void:if _init:return;_init=true
func play(name:String)->void:animation_changed.emit(name)
func _get_configuration_warnings()->PackedStringArray:return[]