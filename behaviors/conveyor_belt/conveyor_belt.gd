## ConveyorBelt — Esteira | Godot 4.7.
@tool
class_name ConveyorBelt
extends Area2D

@export var direction: Vector2 = Vector2(100, 0)
@export var target_group: String = ""

var _bodies: Array[Node2D] = []
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_setup_shape(); body_entered.connect(func(b): _bodies.append(b))
	body_exited.connect(func(b): _bodies.erase(b)); _initialized = true

func _setup_shape() -> void:
	for c in get_children():
		if c is CollisionShape2D: return
	var s := CollisionShape2D.new(); s.name = "BeltShape"
	s.shape = RectangleShape2D.new(); (s.shape as RectangleShape2D).size = Vector2(256,32); add_child(s)

func _physics_process(delta: float) -> void:
	_bodies = _bodies.filter(func(b): return is_instance_valid(b))
	for body in _bodies:
		if not target_group.is_empty() and not body.is_in_group(target_group): continue
		if body is CharacterBody2D:
			(body as CharacterBody2D).velocity += direction * delta
		elif body is RigidBody2D:
			(body as RigidBody2D).apply_central_force(direction * 10)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("Consider setting collision_mask to detect specific layers.")
	return w
