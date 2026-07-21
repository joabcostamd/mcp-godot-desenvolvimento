## WaveSystem — Sistema de Ondas | Godot 4.7.
##
## @tool
class_name WaveSystem
extends Node

@export var total_waves: int = 10: set(v): total_waves=clampi(v,1,100)
@export var spawn_interval: float = 1.0: set(v): spawn_interval=clampf(v,0.1,10.0)
@export var wave_duration: float = 30.0: set(v): wave_duration=clampf(v,5.0,300.0)
@export var rest_duration: float = 5.0: set(v): rest_duration=clampf(v,0.0,60.0)
@export var enemies_per_wave_base: int = 5: set(v): enemies_per_wave_base=clampi(v,1,500)
@export var enemies_increment: int = 3: set(v): enemies_increment=clampi(v,0,100)

signal wave_started(wave_number: int)
signal wave_cleared(wave_number: int)
signal spawn_enemy(wave_number: int)
signal all_waves_cleared()

var _current_wave: int = 0
var _spawn_timer: float = 0.0
var _wave_timer: float = 0.0
var _rest_timer: float = 0.0
var _enemies_spawned: int = 0
var _state: String = "idle"  # idle, spawning, resting
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_initialized = true

func _process(delta: float) -> void:
	match _state:
		"spawning": _process_spawning(delta)
		"resting": _process_resting(delta)

func start() -> void:
	_current_wave = 1
	_start_wave()

func _start_wave() -> void:
	_state = "spawning"
	_spawn_timer = 0.0
	_wave_timer = 0.0
	_enemies_spawned = 0
	wave_started.emit(_current_wave)

func _process_spawning(delta: float) -> void:
	_wave_timer += delta
	_spawn_timer += delta

	if _wave_timer >= wave_duration:
		_end_wave()
		return

	var enemies_this_wave := enemies_per_wave_base + enemies_increment * (_current_wave - 1)
	if _enemies_spawned < enemies_this_wave and _spawn_timer >= spawn_interval:
		_spawn_timer = 0.0
		_enemies_spawned += 1
		spawn_enemy.emit(_current_wave)

func _end_wave() -> void:
	wave_cleared.emit(_current_wave)
	if _current_wave >= total_waves:
		_state = "idle"
		all_waves_cleared.emit()
	else:
		_current_wave += 1
		_state = "resting"
		_rest_timer = 0.0

func _process_resting(delta: float) -> void:
	_rest_timer += delta
	if _rest_timer >= rest_duration:
		_start_wave()

func get_current_wave() -> int: return _current_wave
func get_total_waves() -> int: return total_waves
func get_state() -> String: return _state

func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if total_waves == 1: w.append("Apenas 1 onda configurada.")
	return w
