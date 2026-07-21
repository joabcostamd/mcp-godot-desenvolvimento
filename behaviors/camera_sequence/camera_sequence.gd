@tool class_name CameraSequence extends Node
@export var shots: Array = []
signal shot_changed(index: int)
signal sequence_finished()
var _current_shot: int = -1
var _playing: bool = false
var _camera: Camera2D = null
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	var p:=get_parent()
	if p is Camera2D: _camera=p as Camera2D
	_initialized=true
func play() -> void:
	if _playing or shots.is_empty(): return
	_current_shot=-1; _playing=true; _next_shot()
func _next_shot() -> void:
	_current_shot+=1
	if _current_shot>=shots.size(): _playing=false; sequence_finished.emit(); return
	shot_changed.emit(_current_shot)
func next_shot() -> void: if _playing: _next_shot()
func stop() -> void: _playing=false
func is_playing() -> bool: return _playing
func get_shot(index: int) -> Dictionary:
	if index<0 or index>=shots.size(): return {}
	return shots[index] as Dictionary
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not _camera: w.append("Parent não é Camera2D.")
	if shots.is_empty(): w.append("shots vazio.")
	return w
