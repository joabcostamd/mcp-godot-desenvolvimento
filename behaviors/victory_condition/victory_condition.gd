## VictoryCondition — Condição de Vitória | Godot 4.7.
##
## Node que monitora condição de vitória e emite victory_achieved.
## check() manual ou conecte inimigos/sinais para detecção automática.
##
## @behavior: victory_condition
## @genres: generic
## @tutorial: behaviors/victory_condition/README.md

@tool
class_name VictoryCondition
extends Node

enum ConditionType { ALL_ENEMIES_DEAD, SCORE_REACHED, TIME_SURVIVED, CUSTOM }

@export var condition_type: ConditionType = ConditionType.ALL_ENEMIES_DEAD
@export var target_value: float = 0.0
@export var enemy_group: String = "enemies"

signal victory_achieved()

var _achieved: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_initialized = true
	if condition_type == ConditionType.ALL_ENEMIES_DEAD:
		_check_enemies_dead()


func _check_enemies_dead() -> void:
	# Verifica em loop até não ter inimigos
	var timer := Timer.new()
	timer.wait_time = 1.0
	timer.one_shot = false
	timer.timeout.connect(_poll_enemies)
	add_child(timer)
	timer.start()


func _poll_enemies() -> void:
	if _achieved: return
	var enemies := get_tree().get_nodes_in_group(enemy_group)
	if enemies.is_empty():
		_trigger_victory()


## Força verificação manual. Útil para score_reached e custom.
func check(current_value: float = 0.0) -> void:
	if _achieved: return

	match condition_type:
		ConditionType.SCORE_REACHED, ConditionType.TIME_SURVIVED:
			if current_value >= target_value:
				_trigger_victory()
		ConditionType.CUSTOM:
			_trigger_victory()


## Dispara vitória imediatamente.
func trigger() -> void:
	_trigger_victory()


func _trigger_victory() -> void:
	_achieved = true
	victory_achieved.emit()


func is_achieved() -> bool:
	return _achieved


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
