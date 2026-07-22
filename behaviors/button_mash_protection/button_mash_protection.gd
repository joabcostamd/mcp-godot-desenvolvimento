## Behavior button_mash_protection para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: button_mash_protection
@tool class_name ButtonMashProtection extends Node
@export var enabled: bool = true
signal protection_activated()
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func activate_protection() -> void: protection_activated.emit()
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not enabled: w.append("ButtonMashProtection desabilitado.")
	return w
