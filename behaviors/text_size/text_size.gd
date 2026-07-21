@tool class_name TextSize extends Node
@export var scale_multiplier: float = 1.0: set(v)=scale_multiplier=clampf(v,0.5,3.0)
signal size_changed()
func _ready() -> void: pass
