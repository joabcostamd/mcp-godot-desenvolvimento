@tool
class_name PatrolRoute
extends Node

@export var speed: float = 80.0: set(v): speed=clampf(v,10,1000)
@export var wait_time: float = 1.0: set(v): wait_time=clampf(v,0,10); if _wait_timer: _wait_timer.wait_time=wait_time
@export var loop: bool = true

signal waypoint_reached(index: int); signal route_complete()

var _waypoints: Array[Node2D] = []
var _index: int = 0
var _waiting: bool = false
var _wait_timer: Timer
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_wait_timer = Timer.new(); _wait_timer.name = "PatrolWait"; _wait_timer.one_shot = true
	_wait_timer.wait_time = wait_time; _wait_timer.timeout.connect(func(): _waiting=false)
	add_child(_wait_timer); _scan_waypoints(); _initialized = true

func _scan_waypoints() -> void:
	for c in get_children():
		if c is Node2D and c != _wait_timer: _waypoints.append(c as Node2D)

func _physics_process(delta: float) -> void:
	if _waiting or _waypoints.is_empty(): return
	var p := get_parent(); if not p is Node2D: return
	var target := _waypoints[_index].global_position
	(p as Node2D).global_position = (p as Node2D).global_position.move_toward(target, speed * delta)
	if (p as Node2D).global_position.distance_to(target) < 4.0:
		waypoint_reached.emit(_index); _waiting = true; _wait_timer.start()
		_index += 1
		if _index >= _waypoints.size():
			if loop: _index = 0; route_complete.emit()
			else: _index = _waypoints.size() - 1

func add_waypoint(pos: Vector2) -> void:
	var w := Node2D.new(); w.global_position = pos; add_child(w); _waypoints.append(w)

func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if _waypoints.is_empty(): w.append("No waypoints — use add_waypoint() or add Node2D children.")
	return w
