## Behavior screen_shake_toggle para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: screen_shake_toggle
@tool class_name ScreenShakeToggle extends Node
@export var enabled: bool = true
signal toggled()
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func toggle() -> void: enabled=!enabled; toggled.emit()
func _get_configuration_warnings() -> PackedStringArray: return []
