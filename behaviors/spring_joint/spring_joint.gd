## SpringJoint — Junta de Mola | Godot 4.7.
@tool
class_name SpringJoint
extends Node

@export var anchor_a: NodePath = NodePath()
@export var anchor_b: NodePath = NodePath()
@export var stiffness: float = 100.0: set(v): stiffness = clampf(v, 1, 1000)
@export var damping: float = 5.0: set(v): damping = clampf(v, 0, 50)
@export var rest_length: float = 100.0: set(v): rest_length = clampf(v, 1, 1000)

func _physics_process(delta: float) -> void:
	var a := _get_node2d(anchor_a) if not anchor_a.is_empty() else (get_parent() as Node2D if get_parent() is Node2D else null)
	var b := _get_node2d(anchor_b) if not anchor_b.is_empty() else null
	if not a or not b: return
	var diff := a.global_position - b.global_position
	var dist := diff.length()
	if dist < 0.01: return
	var force_dir := diff.normalized()
	var spring_force := force_dir * (dist - rest_length) * stiffness
	var damp_force := (a is CharacterBody2D and b is CharacterBody2D) as bool
	_aplly_force(a, -spring_force)
	_aplly_force(b, spring_force)

func _get_node2d(path: NodePath) -> Node2D:
	return get_node(path) as Node2D if not path.is_empty() else null

func _aplly_force(node: Node2D, force: Vector2) -> void:
	if node is CharacterBody2D: (node as CharacterBody2D).velocity += force * 0.01
	elif node is RigidBody2D: (node as RigidBody2D).apply_central_force(force)
