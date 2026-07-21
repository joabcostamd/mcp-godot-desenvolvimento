@tool class_name GyroAim extends Node
@export var sensitivity: float = 1.0: set(v)=sensitivity=clampf(v,0.1,5.0)
@export var smoothing: float = 0.8: set(v)=smoothing=clampf(v,0.0,1.0)
signal gyro_active()
var _initialized: bool = false; var _smoothed: Vector2
func _ready() -> void: if _initialized: return; _initialized=true
func process_gyro(gyro: Vector2) -> Vector2:
	_smoothed=_smoothed.lerp(gyro*sensitivity,1.0-smoothing); gyro_active.emit(); return _smoothed
func _get_configuration_warnings() -> PackedStringArray: return []
