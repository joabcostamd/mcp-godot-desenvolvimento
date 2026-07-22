## Behavior analytics_tracker para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: analytics_tracker
@tool class_name AnalyticsTracker extends Node
@export var tracking_id: String = ""
signal event_tracked(event_name: String, properties: Dictionary); signal batch_sent()
var _events: Array[Dictionary] = []; var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func track_event(event_name: String, properties: Dictionary={}) -> void: _events.append({"name":event_name,"props":properties}); event_tracked.emit(event_name,properties)
func flush() -> void: _events.clear(); batch_sent.emit()
func _get_configuration_warnings() -> PackedStringArray: return []
