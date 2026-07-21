@tool class_name TextSize extends Node
@export var scale_multiplier: float = 1.0:
	set(v):
		scale_multiplier=clampf(v,0.5,3.0)
		size_changed.emit()
signal size_changed()
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func _get_configuration_warnings() -> PackedStringArray: return []
