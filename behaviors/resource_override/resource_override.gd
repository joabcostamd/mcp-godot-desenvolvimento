@tool class_name ResourceOverride extends Node; signal resource_overridden(path: String); signal override_cleared()
var _overrides: Dictionary = {}; var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func override(path: String) -> void: _overrides[path]=true; resource_overridden.emit(path)
func clear() -> void: _overrides.clear(); override_cleared.emit()
func _get_configuration_warnings() -> PackedStringArray: return []