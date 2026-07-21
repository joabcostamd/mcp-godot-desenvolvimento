@tool class_name PatchSystem extends Node; signal patch_applied(version: String); signal patch_failed(version: String)
var _initialized: bool = false; func _ready() -> void: if _initialized: return; _initialized=true
func apply_patch(version: String) -> void: patch_applied.emit(version)
func fail_patch(v:String)->void:patch_failed.emit(v)
func _get_configuration_warnings() -> PackedStringArray: return []