## Node que gerencia curva de dificuldade progressiva.
## Generos: survivors_like, generic.
## Tags: dificuldade, curva, estrutura.
## Extends: Node.
## Sinais: difficulty_changed().
## Dependencias: nenhuma.
## @behavior: difficulty_curve
@tool class_name DifficultyCurve extends Node
@export var start_multiplier: float = 1.0: set(v): start_multiplier=clampf(v,0.1,10.0)
@export var increase_per_minute: float = 0.1: set(v): increase_per_minute=clampf(v,0.0,5.0)
@export var max_multiplier: float = 10.0: set(v): max_multiplier=clampf(v,1.0,100.0)
signal difficulty_changed(multiplier: float)
var _elapsed: float = 0.0
var _current: float = 1.0
var _last_emitted: float = 1.0
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	_current = start_multiplier
	_last_emitted = _current
	_initialized = true
func _process(delta: float) -> void:
	_elapsed += delta
	_current = minf(start_multiplier + increase_per_minute * (_elapsed / 60.0), max_multiplier)
	if absf(_current - _last_emitted) >= 0.1:
		_last_emitted = _current
		difficulty_changed.emit(_current)
func get_multiplier() -> float: return _current
func reset() -> void: _elapsed=0.0; _current=start_multiplier
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if increase_per_minute == 0.0: w.append("increase_per_minute=0 — dificuldade nunca aumenta.")
	return w
