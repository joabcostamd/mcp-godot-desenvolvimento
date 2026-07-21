## DayNightCycle — Ciclo Dia-Noite | Godot 4.7 Style Guide compliant.
##
## _process interpola 0→1 sobre cycle_duration. Emite time_changed e
## phase_changed (dawn/day/dusk/night). auto_start inicia automaticamente.
##
## @behavior: day_night_cycle
## @genres: generic
## @tutorial: behaviors/day_night_cycle/README.md

@tool
class_name DayNightCycle
extends Node

enum Phase { DAWN, DAY, DUSK, NIGHT }

@export var cycle_duration: float = 300.0: set(v): cycle_duration = clampf(v, 10, 86400)
@export var auto_start: bool = true

signal time_changed(time: float)
signal phase_changed(phase: String)

var _elapsed: float = 0.0
var _active: bool = false
var _last_phase: int = -1


func _ready() -> void:
	if auto_start: start()


func _process(delta: float) -> void:
	if not _active: return
	_elapsed += delta
	if _elapsed >= cycle_duration:
		_elapsed = fmod(_elapsed, cycle_duration)

	var t := _elapsed / cycle_duration
	time_changed.emit(t)

	var phase_idx := _get_phase_index(t)
	if phase_idx != _last_phase:
		_last_phase = phase_idx
		phase_changed.emit(_phase_name(phase_idx))


func _get_phase_index(t: float) -> int:
	if t < 0.25: return Phase.DAWN
	if t < 0.5: return Phase.DAY
	if t < 0.75: return Phase.DUSK
	return Phase.NIGHT


func _phase_name(idx: int) -> String:
	match idx:
		Phase.DAWN: return "dawn"
		Phase.DAY: return "day"
		Phase.DUSK: return "dusk"
		Phase.NIGHT: return "night"
	return "day"


func start() -> void:
	_active = true


func stop() -> void:
	_active = false


func get_time() -> float:
	return _elapsed / cycle_duration if cycle_duration > 0 else 0.0


func get_phase() -> String:
	return _phase_name(_get_phase_index(get_time()))


func is_active() -> bool:
	return _active
