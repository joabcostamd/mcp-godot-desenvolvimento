## Burnable — Inflamável | Godot 4.7.
##
## Node que detecta dano de fogo no Health sibling e inicia queima.
## Dano contínuo por burn_duration. Pode espalhar para vizinhos.

@tool
class_name Burnable
extends Node

@export var ignition_time: float = 0.5: set(v): ignition_time = clampf(v, 0, 5)
@export var burn_duration: float = 5.0: set(v): burn_duration = clampf(v, 0.5, 30)
@export var burn_dps: float = 10.0: set(v): burn_dps = clampf(v, 1, 500)
@export var spread_radius: float = 100.0: set(v): spread_radius = clampf(v, 0, 500)

signal ignited()
signal extinguished()
signal burned_out()

var _health: Health = null
var _burning: bool = false
var _burn_timer: float = 0.0
var _ignition_timer: float = 0.0
var _igniting: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_find_health()
	_initialized = true


func _find_health() -> void:
	var p := get_parent(); if not p: return
	for c in p.get_children():
		if c is Health:
			_health = c as Health
			if not _health.damage_taken.is_connected(_on_damage):
				_health.damage_taken.connect(_on_damage)
			return


func _on_damage(_amount: int, _current: int, hit_type: String = "") -> void:
	if _burning or _igniting: return
	if hit_type == "fire": _start_ignition()


func _physics_process(delta: float) -> void:
	if _igniting:
		_ignition_timer += delta
		if _ignition_timer >= ignition_time:
			_igniting = false; _start_burn()

	if _burning:
		_burn_timer += delta
		if _health: _health.take_damage(int(burn_dps * delta), "fire")
		if _burn_timer >= burn_duration:
			_burning = false; burned_out.emit()
		elif spread_radius > 0: _try_spread()


func _start_ignition() -> void:
	_igniting = true; _ignition_timer = 0.0


func _start_burn() -> void:
	_burning = true; _burn_timer = 0.0; ignited.emit()


func extinguish() -> void:
	_igniting = false; _burning = false
	extinguished.emit()


func _try_spread() -> void:
	var p := get_parent(); if not p or not p is Node2D: return
	var space := (p as Node2D).get_world_2d().direct_space_state
	if not space: return
	var q := PhysicsShapeQueryParameters2D.new()
	var shape := CircleShape2D.new(); shape.radius = spread_radius
	q.shape = shape; q.transform = Transform2D(0, (p as Node2D).global_position)
	for result in space.intersect_shape(q, 1):
		var collider := result.get("collider")
		if collider and collider is Node:
			for c in (collider as Node).get_children():
				if c is Burnable and c != self: (c as Burnable)._start_ignition()


func is_burning() -> bool: return _burning


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
