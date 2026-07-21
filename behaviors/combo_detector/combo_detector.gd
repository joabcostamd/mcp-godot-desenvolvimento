## Behavior Combo Detector para Godot 4.
## Generos: fighting.
## Tags: input.
## Extends: Node.
## Sinais: combo_started(), combo_advanced(), combo_finished(), combo_dropped().
## Dependencias: nenhuma.
## @behavior: combo_detector
@tool class_name ComboDetector extends Node
@export var time_window: float = 1.0: set(v)=time_window=clampf(v,0.1,5.0)
signal combo_started(); signal combo_advanced(step: int); signal combo_finished(sequence: String); signal combo_dropped()
var _sequence: Array[String] = []; var _current_step: int = 0; var _last_input: float = 0.0; var _active: bool = false
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func set_sequence(seq: Array[String]) -> void: _sequence=seq; _current_step=0; _active=false
func register_input(action: String) -> void:
	var t:=Time.get_ticks_msec()/1000.0
	if _active and t-_last_input>time_window: _active=false; _current_step=0; combo_dropped.emit()
	if _current_step>=_sequence.size(): _current_step=0
	if _sequence.is_empty(): return
	if action==_sequence[_current_step]:
		if _current_step==0: _active=true; combo_started.emit()
		_current_step+=1; _last_input=t; combo_advanced.emit(_current_step)
		if _current_step>=_sequence.size(): combo_finished.emit("_".join(_sequence)); _current_step=0; _active=false
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if _sequence.is_empty(): w.append("sequence vazio.")
	return w
