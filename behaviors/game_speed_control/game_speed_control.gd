@tool class_name GameSpeedControl extends Node
@export var speed_multiplier: float = 1.0: set(v)=speed_multiplier=clampf(v,0.25,4.0)
signal speed_changed()
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func set_speed(s: float) -> void: speed_multiplier=s; Engine.time_scale=s; speed_changed.emit()
func _get_configuration_warnings() -> PackedStringArray: return []
