## Behavior narrative_replay para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: narrative_replay
@tool class_name NarrativeReplay extends Node
signal replayed()
var _init:=false
func _ready()->void:if _init:return;_init=true
func replay()->void:replayed.emit()
func _get_configuration_warnings()->PackedStringArray:return[]