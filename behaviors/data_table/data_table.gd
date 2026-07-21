@tool class_name DataTable extends Resource
signal data_changed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]