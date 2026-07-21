@tool class_name ResourceFactory extends Node
signal resource_created();signal resource_cached()
var _init:=false
func _ready()->void:if _init:return;_init=true
func create()->void:resource_created.emit()
func cache()->void:resource_cached.emit()
func _get_configuration_warnings()->PackedStringArray:return[]