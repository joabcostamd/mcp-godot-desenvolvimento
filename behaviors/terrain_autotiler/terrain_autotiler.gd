@tool class_name TerrainAutotiler extends Node
signal terrain_painted();signal auto_tiled()
var _init:=false
func _ready()->void:if _init:return;_init=true
func paint()->void:terrain_painted.emit()
func auto_tile()->void:auto_tiled.emit()
func _get_configuration_warnings()->PackedStringArray:return[]