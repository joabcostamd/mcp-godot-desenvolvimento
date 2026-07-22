## Behavior hold_alternative para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: hold_alternative
@tool class_name HoldAlternative extends Node
@export var hold_threshold: float = 0.5: set(v)=hold_threshold=clampf(v,0.1,5.0)
signal alternative_triggered()
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func trigger_alternative() -> void: alternative_triggered.emit()
func _get_configuration_warnings() -> PackedStringArray: return []
