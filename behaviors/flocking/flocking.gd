## Flocking — Comportamento de Bando (Boids) | Godot 4.7.
##
## Node filho de CharacterBody2D que aplica 3 forças de steering:
## separação, alinhamento e coesão. Vizinhos detectados via grupo.
##
## @behavior: flocking
## @genres: topdown_shooter, simulation, bullet_hell, roguelike, generic
## @tutorial: behaviors/flocking/README.md

@tool
class_name Flocking
extends Node

@export var separation_weight: float = 1.5:
	set(v): separation_weight = clampf(v, 0.0, 10.0)
@export var alignment_weight: float = 1.0:
	set(v): alignment_weight = clampf(v, 0.0, 10.0)
@export var cohesion_weight: float = 1.0:
	set(v): cohesion_weight = clampf(v, 0.0, 10.0)
@export var neighbor_radius: float = 100.0:
	set(v): neighbor_radius = clampf(v, 10.0, 1000.0)
@export var max_speed: float = 150.0:
	set(v): max_speed = clampf(v, 10.0, 2000.0)
@export var flock_group: String = "flock"


func _physics_process(_delta: float) -> void:
	var parent := get_parent()
	if not parent is CharacterBody2D:
		return

	var neighbors := _get_neighbors(parent)
	if neighbors.is_empty():
		return

	var separation := _separation(parent, neighbors) * separation_weight
	var alignment := _alignment(neighbors) * alignment_weight
	var cohesion := _cohesion(parent, neighbors) * cohesion_weight

	var steering := separation + alignment + cohesion
	if steering.length() > 0.01:
		parent.velocity = steering.normalized() * max_speed


func _get_neighbors(self_body: CharacterBody2D) -> Array[CharacterBody2D]:
	var all := get_tree().get_nodes_in_group(flock_group)
	var neighbors: Array[CharacterBody2D] = []
	for node in all:
		if node == self_body or not node is CharacterBody2D:
			continue
		if self_body.global_position.distance_to(node.global_position) <= neighbor_radius:
			neighbors.append(node)
	return neighbors


func _separation(self_body: CharacterBody2D, neighbors: Array[CharacterBody2D]) -> Vector2:
	var force := Vector2.ZERO
	var count := 0
	for n in neighbors:
		var to_neighbor := self_body.global_position - n.global_position
		var dist := to_neighbor.length()
		if dist < 0.01:
			continue
		force += to_neighbor.normalized() / dist
		count += 1
	if count == 0:
		return Vector2.ZERO
	return force / float(count)


func _alignment(neighbors: Array[CharacterBody2D]) -> Vector2:
	var avg_velocity := Vector2.ZERO
	var count := 0
	for n in neighbors:
		avg_velocity += n.velocity
		count += 1
	if count == 0:
		return Vector2.ZERO
	return avg_velocity / float(count)


func _cohesion(self_body: CharacterBody2D, neighbors: Array[CharacterBody2D]) -> Vector2:
	var center := Vector2.ZERO
	var count := 0
	for n in neighbors:
		center += n.global_position
		count += 1
	if count == 0:
		return Vector2.ZERO
	center /= float(count)
	return (center - self_body.global_position).normalized()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	var parent := get_parent()
	if parent and not parent is CharacterBody2D:
		w.append("O pai deve ser CharacterBody2D para o movimento funcionar.")
	if flock_group.is_empty():
		w.append("flock_group está vazio — nenhum vizinho será encontrado.")
	return w
