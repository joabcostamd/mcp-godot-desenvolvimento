@tool class_name LodController extends Node
signal lod_changed(level:int)
var _init:=false
func _ready()->void:if _init:return;_init=true
func set_lod(l:int)->void:lod_changed.emit(l)
func _get_configuration_warnings()->PackedStringArray:return[]