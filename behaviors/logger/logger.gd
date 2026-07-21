@tool class_name Logger extends Node
@export var log_level: String = "info"
signal log_written(level: String, message: String)
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func log(level: String, message: String) -> void: log_written.emit(level,message); print("[%s] %s" % [level.to_upper(),message])
func info(msg: String) -> void: log("info",msg)
func warn(msg: String) -> void: log("warn",msg)
func error(msg: String) -> void: log("error",msg)
func _get_configuration_warnings() -> PackedStringArray: return []
