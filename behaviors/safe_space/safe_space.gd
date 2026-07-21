@tool class_name SafeSpace extends Node
signal warning_shown();signal content_skipped()
var _init:=false
func _ready()->void:if _init:return;_init=true
func show_warning()->void:warning_shown.emit()
func skip()->void:content_skipped.emit()
func _get_configuration_warnings()->PackedStringArray:return[]