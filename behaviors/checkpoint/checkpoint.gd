## Checkpoint — Ponto de Salvamento | Godot 4.7 Style Guide compliant.
##
## Area2D que salva posição do player via SaveLoad ao ser ativado.
## respawn() estático teleporta para o último checkpoint salvo.
##
## @behavior: checkpoint
## @genres: platformer, topdown_shooter, metroidvania, generic
## @tutorial: behaviors/checkpoint/README.md

@tool
class_name Checkpoint
extends Area2D

@export var checkpoint_id: String = "default"
@export var spawn_offset: Vector2 = Vector2.ZERO

signal checkpoint_reached(checkpoint_id: String)

var _activated: bool = false
var _initialized: bool = false

static var _last_checkpoint_data: Dictionary = {}


func _ready() -> void:
	if _initialized: return
	_setup_collision()
	body_entered.connect(_on_body_entered)
	_initialized = true


func _setup_collision() -> void:
	var shape := CollisionShape2D.new()
	shape.name = "CheckpointShape"
	var rect := RectangleShape2D.new()
	rect.size = Vector2(64, 64)
	shape.shape = rect
	add_child(shape)


func _on_body_entered(body: Node2D) -> void:
	if _activated: return
	_activated = true
	_save_position(body.global_position + spawn_offset)
	checkpoint_reached.emit(checkpoint_id)


func _save_position(pos: Vector2) -> void:
	_last_checkpoint_data["position_x"] = pos.x
	_last_checkpoint_data["position_y"] = pos.y
	_last_checkpoint_data["checkpoint_id"] = checkpoint_id

	var sl := _find_save_load()
	if sl and sl.has_method("set_data"):
		sl.set_data("checkpoint_x", pos.x)
		sl.set_data("checkpoint_y", pos.y)
		sl.set_data("checkpoint_id", checkpoint_id)


func _find_save_load() -> Node:
	var tree := get_tree()
	if tree:
		for node in tree.get_nodes_in_group("save_load"):
			if node.has_method("set_data"):
				return node
	return null


## Teleporta o player para o último checkpoint (estático).
static func respawn(player: Node2D) -> void:
	if _last_checkpoint_data.is_empty():
		return
	var x: float = _last_checkpoint_data.get("position_x", 0.0)
	var y: float = _last_checkpoint_data.get("position_y", 0.0)
	player.global_position = Vector2(x, y)


func is_activated() -> bool:
	return _activated


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("Consider setting collision_mask to detect specific layers.")
	return w
