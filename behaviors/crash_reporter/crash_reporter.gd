## Behavior crash_reporter para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: crash_reporter
@tool class_name CrashReporter extends Node
@export var dsn_url: String = ""
signal crash_captured(error: String); signal report_sent(); signal report_failed()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func capture_error(error_msg: String) -> void: crash_captured.emit(error_msg)
func send_report() -> void: report_sent.emit()
func fail_report()->void:report_failed.emit()
func _get_configuration_warnings() -> PackedStringArray: return []
