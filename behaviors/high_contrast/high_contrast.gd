@tool class_name HighContrast extends Node
@export var contrast_level: float = 1.0: set(v)=contrast_level=clampf(v,0.5,3.0)
signal contrast_changed()
func _ready() -> void: pass
