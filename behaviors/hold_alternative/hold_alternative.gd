@tool class_name HoldAlternative extends Node
@export var hold_threshold: float = 0.5: set(v)=hold_threshold=clampf(v,0.1,5.0)
signal alternative_triggered()
func _ready() -> void: pass
