@tool class_name ProfilerHook extends Node
@export var auto_start: bool = false
signal profiling_started(); signal profiling_stopped()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true; if auto_start: start()
func start() -> void: profiling_started.emit()
func stop() -> void: profiling_stopped.emit()
func _get_configuration_warnings() -> PackedStringArray: return []
