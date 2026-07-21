@tool class_name TilemapLayerManager extends Node
signal layer_added();signal layer_removed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func _get_configuration_warnings()->PackedStringArray:return[]