@tool class_name StereoToMono extends Node
var _init:=false;@export var enabled:bool=true
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]