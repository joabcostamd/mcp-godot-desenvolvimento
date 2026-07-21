@tool class_name SaveIntegrity extends Node
signal integrity_verified(); signal corruption_detected()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func verify(path: String) -> bool:
	if not FileAccess.file_exists(path): corruption_detected.emit(); return false
	integrity_verified.emit(); return true
func checksum(data: String) -> String: return str(data.hash())
func _get_configuration_warnings() -> PackedStringArray: return []
