@tool class_name ModSandbox extends Node; signal sandbox_violation(rule: String)
var _initialized: bool = false; func _ready() -> void: if _initialized: return; _initialized=true
func report_violation(rule: String) -> void: sandbox_violation.emit(rule)
func _get_configuration_warnings() -> PackedStringArray: return []