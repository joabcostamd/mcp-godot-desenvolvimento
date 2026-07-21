@tool
class_name Pathfinding
extends Node

@export var speed: float = 150.0: set(v): speed=clampf(v,10,2000)
@export var arrival_distance: float = 8.0: set(v): arrival_distance=clampf(v,4,64)
@export var avoidance_enabled: bool = true

signal path_found(); signal path_lost(); signal arrived()

var _agent: NavigationAgent2D
var _target: Vector2 = Vector2.INF
var _arrived_emitted: bool = false
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_agent = NavigationAgent2D.new(); _agent.name = "NavAgent"
	_agent.avoidance_enabled = avoidance_enabled
	add_child(_agent); _initialized = true

func _physics_process(_delta: float) -> void:
	var p := get_parent(); if not p is CharacterBody2D: return
	if _target == Vector2.INF: return
	var body := p as CharacterBody2D
	var next := _agent.get_next_path_position()
	var dir := body.global_position.direction_to(next)
	body.velocity = dir * speed
	body.move_and_slide()
	if body.global_position.distance_to(_target) < arrival_distance:
		if not _arrived_emitted: arrived.emit(); _arrived_emitted = true
	else:
		_arrived_emitted = false

func set_target(pos: Vector2) -> void:
	_target = pos; _agent.target_position = pos
	_arrived_emitted = false; path_found.emit()

func clear_target() -> void:
	_target = Vector2.INF; path_lost.emit()

func get_target() -> Vector2: return _target
func is_navigating() -> bool: return _target != Vector2.INF

func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	var p := get_parent(); if not p is CharacterBody2D: w.append("Parent must be CharacterBody2D.")
	return w
