## Buoyancy — Flutuabilidade | Godot 4.7.
@tool
class_name Buoyancy
extends Area2D

@export var fluid_density: float = 1.0: set(v): fluid_density = clampf(v, 0.1, 5)
@export var drag_coefficient: float = 0.5: set(v): drag_coefficient = clampf(v, 0, 2)
@export var surface_y: float = 0.0

signal entered_fluid(body: Node2D)
signal exited_fluid(body: Node2D)
var _bodies: Array[Node2D] = []
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return; _setup_shape()
	body_entered.connect(func(b): _bodies.append(b); entered_fluid.emit(b))
	body_exited.connect(func(b): _bodies.erase(b); exited_fluid.emit(b)); _initialized = true

func _setup_shape() -> void:
	for c in get_children():
		if c is CollisionShape2D: return
	var s := CollisionShape2D.new(); s.name = "FluidShape"
	s.shape = RectangleShape2D.new(); (s.shape as RectangleShape2D).size = Vector2(512,256); add_child(s)

func _physics_process(delta: float) -> void:
	_bodies = _bodies.filter(func(b): return is_instance_valid(b))
	for body in _bodies:
		if not body is CharacterBody2D: continue
		var b := body as CharacterBody2D
		var depth := surface_y - b.global_position.y if surface_y != 0 else b.global_position.y
		if depth > 0: b.velocity.y -= fluid_density * 500 * delta
		b.velocity *= (1.0 - drag_coefficient * delta)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("Consider setting collision_mask to detect specific layers.")
	return w
