@tool class_name AnimationLayer extends Node
signal layer_enabled();signal layer_disabled()
var _init:=false
func _ready()->void:if _init:return;_init=true
func enable()->void:layer_enabled.emit()
func disable()->void:layer_disabled.emit()
func _get_configuration_warnings()->PackedStringArray:return[]