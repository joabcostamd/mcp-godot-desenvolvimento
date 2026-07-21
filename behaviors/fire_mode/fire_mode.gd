## Node que gerencia modos de disparo (auto, burst, semi).
## Generos: topdown_shooter, generic.
## Tags: arma, tiro.
## Extends: Node.
## Sinais: mode_changed().
## Dependencias: fire_rate.
## @behavior: fire_mode
@tool
class_name FireMode
extends Node

enum Mode { AUTO, BURST, SEMI }
@export var mode: int = 0: set(v): mode=clampi(v,0,2); mode_changed.emit(mode)
@export var burst_count: int = 3: set(v): burst_count=clampi(v,2,10)
@export var burst_interval: float = 0.05: set(v): burst_interval=clampf(v,0.02,0.5)

signal mode_changed(new_mode: int)
var _semi_fired: bool = false
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return; _initialized = true

func can_fire() -> bool:
	if mode == Mode.SEMI:
		if _semi_fired: return false
		if Input.is_action_just_pressed("ui_accept"): _semi_fired=true; return true
		return false
	return true

func reset_semi() -> void: _semi_fired = false
func get_burst_count() -> int: return burst_count if mode == Mode.BURST else 1
func get_burst_interval() -> float: return burst_interval if mode == Mode.BURST else 0.0

func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	return w
