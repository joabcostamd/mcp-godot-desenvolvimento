## Behavior Haptic Manager para Godot 4.
## Generos: generic.
## Tags: input.
## Extends: Node.
## Sinais: vibration_started(), vibration_ended().
## Dependencias: nenhuma.
## @behavior: haptic_manager
@tool class_name HapticManager extends Node
@export var intensity: float = 1.0: set(v)=intensity=clampf(v,0.0,2.0)
signal vibration_started(); signal vibration_ended()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func vibrate(weak_magnitude: float=1.0, strong_magnitude: float=1.0, duration: float=0.1) -> void:
	Input.start_joy_vibration(0,weak_magnitude*intensity,strong_magnitude*intensity,duration)
	vibration_started.emit()
func stop_vibration() -> void: Input.stop_joy_vibration(0); vibration_ended.emit()
func _get_configuration_warnings() -> PackedStringArray: return []
