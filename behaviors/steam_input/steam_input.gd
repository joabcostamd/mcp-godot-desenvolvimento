@tool class_name SteamInput extends Node
@export var action_set: String = "default"
signal action_set_changed(new_set: String)
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func set_action_set(set_name: String) -> void: action_set=set_name; action_set_changed.emit(set_name)
func _get_configuration_warnings() -> PackedStringArray: return []
