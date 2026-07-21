@tool class_name CurveTable extends Resource
signal curve_updated()
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]