@tool class_name CloudSave extends Node
@export var provider: String = "steam"
signal synced(); signal sync_failed()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func sync() -> void: synced.emit()
func _get_configuration_warnings() -> PackedStringArray: return []
