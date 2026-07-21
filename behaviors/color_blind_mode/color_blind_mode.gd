@tool class_name ColorBlindMode extends Node
@export var mode: int = 0: set(v)=mode=clampi(v,0,3); mode_changed.emit(mode)
@export var intensity: float = 0.8: set(v)=intensity=clampf(v,0.0,1.0)
signal mode_changed(new_mode: int)
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func apply() -> void: pass
func _get_configuration_warnings() -> PackedStringArray: return []
