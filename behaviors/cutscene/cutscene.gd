@tool class_name Cutscene extends Node
signal cutscene_started()
signal cutscene_ended()
signal step_executed(step_index: int)
var _steps: Array = []
var _current_step: int = -1
var _playing: bool = false
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func add_step(step: Dictionary) -> void: _steps.append(step)
func play() -> void:
	if _playing: return
	_current_step=-1; _playing=true; cutscene_started.emit(); _advance()
func _advance() -> void:
	_current_step+=1
	if _current_step>=_steps.size(): _playing=false; cutscene_ended.emit(); return
	step_executed.emit(_current_step)
func next_step() -> void: if _playing: _advance()
func skip() -> void: _playing=false; cutscene_ended.emit()
func is_playing() -> bool: return _playing
func get_current_step_index() -> int: return _current_step
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if _steps.is_empty(): w.append("Nenhum step — cutscene vazia.")
	return w
