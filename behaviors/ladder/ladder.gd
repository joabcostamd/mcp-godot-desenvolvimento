## Ladder — Escada | Godot 4.7.
##
## Area2D que permite subir/descer. Override de gravidade
## enquanto o player está dentro e pressiona ui_up/ui_down.

@tool
class_name Ladder
extends Area2D

@export var climb_speed: float = 150.0:
	set(v): climb_speed = clampf(v, 10, 1000)
@export var player_group: String = "players"

signal climbing_started(body: Node2D)
signal climbing_ended(body: Node2D)

var _climbers: Dictionary = {}  # body -> is_climbing
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_setup_shape()
	body_entered.connect(func(b): _on_enter(b))
	body_exited.connect(func(b): _on_exit(b))
	_initialized = true


func _setup_shape() -> void:
	for c in get_children():
		if c is CollisionShape2D: return
	var s := CollisionShape2D.new(); s.name = "LadderShape"
	var r := RectangleShape2D.new(); r.size = Vector2(32, 128)
	s.shape = r; add_child(s)


func _physics_process(_delta: float) -> void:
	for body in _climbers.keys():
		if not is_instance_valid(body):
			_climbers.erase(body); continue
		var was_climbing := _climbers[body] as bool
		if not body.is_in_group(player_group): continue
		var vert := Input.get_axis("ui_up", "ui_down")
		if vert == 0.0 and not _is_overlapping_body(body):
			if was_climbing: _stop_climb(body); continue
		if vert != 0.0:
			if body is CharacterBody2D:
				(body as CharacterBody2D).velocity.y = -vert * climb_speed
			if not was_climbing: _start_climb(body)


func _on_enter(body: Node2D) -> void:
	if not body.is_in_group(player_group): return
	_climbers[body] = false


func _on_exit(body: Node2D) -> void:
	if _climbers.get(body, false): _stop_climb(body)
	_climbers.erase(body)


func _start_climb(body: Node2D) -> void:
	_climbers[body] = true; climbing_started.emit(body)


func _stop_climb(body: Node2D) -> void:
	_climbers[body] = false; climbing_ended.emit(body)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("Consider setting collision_mask to detect specific layers.")
	return w
