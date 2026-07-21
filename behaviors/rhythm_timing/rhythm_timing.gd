@tool class_name RhythmTiming extends Node
@export var bpm: float = 120.0: set(v): bpm=clampf(v,30,300)
@export var tolerance: float = 0.1: set(v): tolerance=clampf(v,0.01,0.5)
@export var input_action: String = "ui_accept"
signal perfect(); signal good(); signal miss(); signal beat(number: int)
var _beat_interval: float = 0.0; var _timer: float = 0.0; var _beat_count: int = 0
var _next_beat: float = 0.0; var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_beat_interval=60.0/bpm; _next_beat=_beat_interval
	_initialized = true

func _physics_process(delta: float) -> void:
	_timer+=delta
	if _timer>=_next_beat: _beat_count+=1; beat.emit(_beat_count); _next_beat+=_beat_interval
	if Input.is_action_just_pressed(input_action): _check_hit()

func _check_hit() -> void:
	var offset:=abs(_timer-_next_beat+_beat_interval)
	if offset<tolerance*0.5: perfect.emit()
	elif offset<tolerance: good.emit()
	else: miss.emit()
