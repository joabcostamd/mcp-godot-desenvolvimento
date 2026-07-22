## Behavior tilemap_layer_manager para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: tilemap_layer_manager
@tool class_name TilemapLayerManager extends Node
signal layer_added();signal layer_removed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func add_layer()->void:layer_added.emit()
func remove_layer()->void:layer_removed.emit()
func _get_configuration_warnings()->PackedStringArray:return[]