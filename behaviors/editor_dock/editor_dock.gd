@tool class_name EditorDock extends Control; signal dock_added(title: String); signal dock_removed(title: String)
var _initialized: bool = false; func _ready() -> void: if _initialized: return; _initialized=true
func add_dock(title: String) -> void: dock_added.emit(title)
func remove_dock(title: String) -> void: dock_removed.emit(title)
func _get_configuration_warnings() -> PackedStringArray: return []