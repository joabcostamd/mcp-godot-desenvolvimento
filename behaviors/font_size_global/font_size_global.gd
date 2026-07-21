@tool class_name FontSizeGlobal extends Node
signal size_changed()
var _init:=false;@export var scale:float=1.0
func _ready()->void:if _init:return;_init=true
@export var scale:float=1.0:set(v)=scale=v;size_changed.emit()
func _get_configuration_warnings()->PackedStringArray:return[]