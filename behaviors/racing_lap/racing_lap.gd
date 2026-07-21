@tool class_name RacingLap extends Node
@export var total_laps: int = 3: set(v)=total_laps=clampi(v,1,20)
signal lap_completed(lap: int); signal race_finished(best_time: float); signal checkpoint_passed(index: int)
var _current_lap: int = 0; var _checkpoints: int = 0; var _best_time: float = INF
var _race_started: bool = false; var _elapsed: float = 0.0
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func _process(delta: float) -> void: if _race_started: _elapsed+=delta
func start_race() -> void: _current_lap=0; _checkpoints=0; _elapsed=0.0; _race_started=true
func pass_checkpoint(index: int) -> void: checkpoint_passed.emit(index); _checkpoints+=1
func complete_lap() -> void: _current_lap+=1; lap_completed.emit(_current_lap); if _current_lap>=total_laps: _race_started=false; if _elapsed<_best_time: _best_time=_elapsed; race_finished.emit(_best_time)
func get_current_lap() -> int: return _current_lap
func get_elapsed() -> float: return _elapsed
func _get_configuration_warnings() -> PackedStringArray: return []
