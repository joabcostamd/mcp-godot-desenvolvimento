@tool class_name CrossSave extends Node
@export var platforms: Array[String] = ["windows","linux"]
signal cross_synced(); signal merge_conflict()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func sync_across_platforms() -> void: cross_synced.emit()
func report_merge_conflict() -> void: merge_conflict.emit()
func _get_configuration_warnings() -> PackedStringArray: return []
