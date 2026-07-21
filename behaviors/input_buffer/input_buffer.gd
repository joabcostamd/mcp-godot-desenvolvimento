## Behavior Input Buffer para Godot 4.
## Generos: fighting.
## Tags: input.
## Extends: Node.
## Sinais: buffered(), executed().
## Dependencias: nenhuma.
## @behavior: input_buffer
@tool class_name InputBuffer extends Node
@export var buffer_window: float = 0.2: set(v)=buffer_window=clampf(v,0.05,1.0)
@export var max_queue: int = 3: set(v)=max_queue=clampi(v,1,10)
signal buffered(action: String); signal executed(action: String); signal cancelled(action: String)
var _buffer: Array[Dictionary] = []
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func _process(delta: float) -> void:
	var expired:=[]; var t:=Time.get_ticks_msec()/1000.0
	for i in _buffer.size():
		if t-_buffer[i].time>buffer_window: expired.append(i)
	for i in range(expired.size()-1, -1, -1):
		var idx:=expired[i]
		cancelled.emit(_buffer[idx].action)
		_buffer.remove_at(idx)
func push_action(action: String) -> void:
	if _buffer.size()>=max_queue: _buffer.pop_front()
	_buffer.append({"action":action,"time":Time.get_ticks_msec()/1000.0}); buffered.emit(action)
func consume_action(action: String) -> bool:
	for i in _buffer.size():
		if _buffer[i].action==action: _buffer.remove_at(i); executed.emit(action); return true
	return false
func clear() -> void: _buffer.clear()
func _get_configuration_warnings() -> PackedStringArray: return []
