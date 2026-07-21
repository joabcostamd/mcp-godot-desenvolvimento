## GravityZone — Zona de Gravidade | Godot 4.7.
@tool
class_name GravityZone
extends Area2D

@export var gravity_direction: Vector2 = Vector2(0, 1):
	set(v): gravity_direction = v.normalized() if v.length() > 0 else Vector2(0, 1)
@export var gravity_strength: float = 980.0: set(v): gravity_strength = clampf(v, 0, 5000)
@export var override: bool = false

signal entered_zone(body: Node2D)
signal exited_zone(body: Node2D)

var _bodies: Array[Node2D] = []
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_setup_shape(); body_entered.connect(func(b): _bodies.append(b); entered_zone.emit(b))
	body_exited.connect(func(b): _bodies.erase(b); exited_zone.emit(b)); _initialized = true

func _setup_shape() -> void:
	for c in get_children():
		if c is CollisionShape2D: return
	var s := CollisionShape2D.new(); s.name = "GravityShape"
	s.shape = RectangleShape2D.new(); (s.shape as RectangleShape2D).size = Vector2(256,256); add_child(s)

func _physics_process(delta: float) -> void:
	_bodies = _bodies.filter(func(b): return is_instance_valid(b))
	for body in _bodies:
		if not body is CharacterBody2D: continue
		var b := body as CharacterBody2D
		if override: b.velocity.y = 0; b.velocity.x = 0
		b.velocity += gravity_direction * gravity_strength * delta
