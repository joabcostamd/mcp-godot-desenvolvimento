## Magnet — Atração Magnética | Godot 4.7.

@tool
class_name Magnet
extends Area2D

@export var force: float = 500.0: set(v): force = clampf(v, 10, 5000)
@export var target_group: String = ""
@export var falloff: int = 1: set(v): falloff = clampi(v, 0, 2)

signal attracted(body: Node2D)
var _bodies: Array[Node2D] = []
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_setup_shape(); body_entered.connect(func(b): if b not in _bodies: _bodies.append(b))
	body_exited.connect(func(b): _bodies.erase(b)); _initialized = true

func _setup_shape() -> void:
	for c in get_children():
		if c is CollisionShape2D: return
	var s := CollisionShape2D.new(); s.name = "MagnetShape"
	var c := CircleShape2D.new(); c.radius = 128; s.shape = c; add_child(s)

func _physics_process(delta: float) -> void:
	_bodies = _bodies.filter(func(b): return is_instance_valid(b))
	for body in _bodies:
		if not target_group.is_empty() and not body.is_in_group(target_group): continue
		if not body is CharacterBody2D: continue
		var dir := global_position.direction_to(body.global_position)
		var dist := global_position.distance_to(body.global_position)
		var radius := 128.0
		var factor := 1.0
		if falloff == 1: factor = clampf(1.0 - dist / radius, 0.1, 1.0)
		elif falloff == 2: factor = clampf(pow(1.0 - dist / radius, 2), 0.01, 1.0)
		(body as CharacterBody2D).velocity += dir * force * factor * delta
		attracted.emit(body)
