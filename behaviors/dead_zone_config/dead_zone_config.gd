@tool class_name DeadZoneConfig extends Node
@export var dead_zone: float = 0.2: set(v)=dead_zone=clampf(v,0.0,0.9)
signal zone_calibrated()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func apply_dead_zone(input: Vector2) -> Vector2:
	if input.length()<dead_zone: return Vector2.ZERO
	return (input.length()-dead_zone)/(1.0-dead_zone)*input.normalized()
func _get_configuration_warnings() -> PackedStringArray: return []
