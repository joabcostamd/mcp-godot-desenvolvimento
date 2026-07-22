## Behavior High Contrast para Godot 4.
## Generos: generic.
## Tags: acessibilidade.
## Extends: Node.
## Sinais: contrast_changed().
## Dependencias: nenhuma.
## @behavior: high_contrast
@tool class_name HighContrast extends Node
@export var contrast_level: float = 1.0:
	set(v):
		contrast_level=clampf(v,0.5,3.0)
		contrast_changed.emit()
signal contrast_changed()
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func _get_configuration_warnings() -> PackedStringArray: return []
