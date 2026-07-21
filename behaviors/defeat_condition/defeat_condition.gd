## DefeatCondition — Condição de Derrota | Godot 4.7.
##
## Node que monitora condição de derrota (player morto, tempo, custom).
## Polling automático para PLAYER_DEAD; check() manual para outros.
##
## @behavior: defeat_condition
## @genres: generic

@tool
class_name DefeatCondition
extends Node

enum ConditionType { PLAYER_DEAD, TIME_UP, CUSTOM }

@export var condition_type: ConditionType = ConditionType.PLAYER_DEAD
@export var player_group: String = "players"

signal defeat_triggered()

var _triggered: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_initialized = true
	if condition_type == ConditionType.PLAYER_DEAD:
		_poll_players()


func _poll_players() -> void:
	var timer := Timer.new()
	timer.wait_time = 1.0; timer.one_shot = false
	timer.timeout.connect(_check_players)
	add_child(timer); timer.start()


func _check_players() -> void:
	if _triggered: return
	if get_tree().get_nodes_in_group(player_group).is_empty():
		_trigger_defeat()


func check(defeated: bool = true) -> void:
	if _triggered: return
	if defeated: _trigger_defeat()


func trigger() -> void: _trigger_defeat()
func _trigger_defeat() -> void: _triggered = true; defeat_triggered.emit()
func is_triggered() -> bool: return _triggered
