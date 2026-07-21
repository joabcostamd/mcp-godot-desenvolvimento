@tool class_name InterfaceRearrange extends Control
signal rearranged();signal layout_saved()
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]