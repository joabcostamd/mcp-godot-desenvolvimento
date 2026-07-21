@tool class_name AutoloadManager extends Node; signal singleton_added(name: String); signal singleton_removed(name: String)
var _singletons: Dictionary = {}; var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func add(name: String) -> void: _singletons[name]=true; singleton_added.emit(name)
func remove(name: String) -> void: if _singletons.has(name): _singletons.erase(name); singleton_removed.emit(name)
func _get_configuration_warnings() -> PackedStringArray: return []