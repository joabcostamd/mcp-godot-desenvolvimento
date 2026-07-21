## WindZone — Zona de Vento | Godot 4.7.
@tool
class_name WindZone
extends Area2D

@export var wind_direction: Vector2 = Vector2(1, 0):
	set(v): wind_direction = v.normalized() if v.length() > 0 else Vector2(1,0)
@export var wind_strength: float = 300.0: set(v): wind_strength = clampf(v, 10, 5000)
@export var turbulence: float = 0.0: set(v): turbulence = clampf(v, 0, 1)

var _bodies: Array[Node2D] = []
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return; _setup_shape()
	body_entered.connect(func(b): _bodies.append(b))
	body_exited.connect(func(b): _bodies.erase(b)); _initialized = true

func _setup_shape() -> void:
	for c in get_children():
		if c is CollisionShape2D: return
	var s := CollisionShape2D.new(); s.name = "WindShape"
	s.shape = RectangleShape2D.new(); (s.shape as RectangleShape2D).size = Vector2(256,128); add_child(s)

func _physics_process(delta: float) -> void:
	_bodies = _bodies.filter(func(b): return is_instance_valid(b))
	for body in _bodies:
		if not body is CharacterBody2D: continue
		var f := wind_direction * wind_strength
		if turbulence > 0: f += Vector2(randf_range(-1,1), randf_range(-1,1)) * wind_strength * turbulence
		(body as CharacterBody2D).velocity += f * delta


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("Consider setting collision_mask to detect specific layers.")
	return w
