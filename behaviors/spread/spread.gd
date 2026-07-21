## Node que aplica dispersão (spread) a projéteis.
## Generos: topdown_shooter, generic.
## Tags: mira, arma.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: spread
@tool
class_name Spread
extends Node

@export var base_spread: float = 2.0: set(v): base_spread=clampf(v,0,45)
@export var spread_per_shot: float = 1.0: set(v): spread_per_shot=clampf(v,0,20)
@export var max_spread: float = 15.0: set(v): max_spread=clampf(v,0,90)
@export var recovery_speed: float = 10.0: set(v): recovery_speed=clampf(v,0.1,100)

var _current_spread: float = 0.0
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_current_spread = base_spread; _initialized = true

func _process(delta: float) -> void:
	_current_spread = move_toward(_current_spread, base_spread, recovery_speed * delta)

func get_angle() -> float:
	var angle := randf_range(-_current_spread, _current_spread)
	_current_spread = minf(_current_spread + spread_per_shot, max_spread)
	return deg_to_rad(angle)

func reset_spread() -> void: _current_spread = base_spread

func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if max_spread > 45: w.append("max_spread above 45 degrees — very wide cone.")
	return w
