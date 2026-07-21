@tool class_name NetworkSync extends Node
@export var sync_interval: float = 0.1: set(v)=sync_interval=clampf(v,0.01,5.0)
signal synced()
signal desync_detected()
var _timer: float = 0.0
var _sync_properties: Array[String] = []
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func _process(delta: float) -> void:
	if not multiplayer or not multiplayer.multiplayer_peer: return
	_timer+=delta
	if _timer>=sync_interval: _timer=0.0; synced.emit()
func add_sync_property(prop: String) -> void:
	if not prop in _sync_properties: _sync_properties.append(prop)
func get_sync_properties() -> Array[String]: return _sync_properties.duplicate()
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not multiplayer or not multiplayer.multiplayer_peer: w.append("Multiplayer peer não configurado.")
	return w
