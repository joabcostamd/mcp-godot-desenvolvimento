@tool class_name PerformanceMonitor extends Node
@export var sample_rate: float = 0.5: set(v)=sample_rate=clampf(v,0.1,5.0)
signal metric_recorded(fps: float, memory_mb: float)
var _timer: float = 0.0; var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func _process(delta: float) -> void: _timer+=delta; if _timer>=sample_rate: _timer=0.0; metric_recorded.emit(Engine.get_frames_per_second(),OS.get_static_memory_usage()/1048576.0)
func _get_configuration_warnings() -> PackedStringArray: return []
