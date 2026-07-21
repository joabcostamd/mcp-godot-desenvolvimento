@tool class_name SubPlugin extends Node; signal sub_enabled(name: String); signal sub_disabled(name: String)
var _initialized: bool = false; func _ready() -> void: if _initialized: return; _initialized=true
func enable(name: String) -> void: sub_enabled.emit(name)
func disable(name: String) -> void: sub_disabled.emit(name)
func _get_configuration_warnings() -> PackedStringArray: return []