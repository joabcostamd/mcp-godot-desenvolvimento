@tool class_name BehaviorRegistry extends Node; signal installed(id: String); signal updated(id: String); signal removed(id: String)
var _initialized: bool = false; func _ready() -> void: if _initialized: return; _initialized=true
func install(id: String) -> void: installed.emit(id)
func mark_updated(id:String)->void:updated.emit(id)
func mark_removed(id:String)->void:removed.emit(id)
func _get_configuration_warnings() -> PackedStringArray: return []