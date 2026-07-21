## Score — Sistema de Pontuação | Godot 4.7.
##
## Node com add_score, combo multiplier e high_score via SaveLoad.
## combo_window: tempo entre scores para incrementar combo.
##
## @behavior: score
## @genres: generic

@tool
class_name Score
extends Node

@export var combo_multiplier: float = 0.1
@export var combo_window: float = 2.0: set(v): combo_window = clampf(v, 0.1, 30)

signal score_changed(new_score: int)
signal new_high_score(high_score: int)
signal combo_reached(level: int)

var _score: int = 0
var _high_score: int = 0
var _combo_level: int = 0
var _combo_timer: Timer = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_load_high_score()
	_initialized = true


func _load_high_score() -> void:
	var sl := _find_save_load()
	if sl and sl.has_method("get_data"):
		_high_score = sl.get_data("high_score", 0)


func _save_high_score() -> void:
	var sl := _find_save_load()
	if sl and sl.has_method("set_data"):
		sl.set_data("high_score", _high_score)


func _find_save_load() -> Node:
	var tree := get_tree()
	if tree:
		for node in tree.get_nodes_in_group("save_load"):
			if node.has_method("get_data"):
				return node
	return null


func add_score(amount: int) -> void:
	if amount <= 0: return

	_combo_level += 1
	var bonus := int(amount * combo_multiplier * (_combo_level - 1))
	var total := amount + bonus
	_score += total
	score_changed.emit(_score)

	if _combo_level > 1:
		combo_reached.emit(_combo_level)

	if _score > _high_score:
		_high_score = _score
		new_high_score.emit(_high_score)
		_save_high_score()

	_reset_combo_timer()


func _reset_combo_timer() -> void:
	if _combo_timer:
		_combo_timer.queue_free()
	_combo_timer = Timer.new()
	_combo_timer.one_shot = true
	_combo_timer.wait_time = combo_window
	_combo_timer.timeout.connect(_reset_combo)
	add_child(_combo_timer)
	_combo_timer.start()


func _reset_combo() -> void:
	_combo_level = 0


func get_score() -> int: return _score
func get_high_score() -> int: return _high_score
func get_combo() -> int: return _combo_level

func reset_score() -> void:
	_score = 0; _combo_level = 0
	score_changed.emit(0)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
