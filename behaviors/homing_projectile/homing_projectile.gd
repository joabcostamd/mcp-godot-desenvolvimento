## HomingProjectile — Projétil Teleguiado | Godot 4.7.
##
## Area2D que persegue um alvo com steering.
## Use set_target() para definir o alvo.
##
## @behavior: homing_projectile
## @genres: topdown_shooter, bullet_hell, roguelike, generic
## @tutorial: behaviors/homing_projectile/README.md

@tool
class_name HomingProjectile
extends Area2D

@export var speed: float = 300.0:
	set(v): speed = clampf(v, 10.0, 2000.0)
@export var turn_rate: float = 3.0:
	set(v): turn_rate = clampf(v, 0.1, 20.0)
@export var damage: int = 20:
	set(v): damage = clampi(v, 1, 9999)
@export var lifetime: float = 5.0:
	set(v): lifetime = clampf(v, 0.0, 60.0)

signal hit(target: Node, damage_dealt: int)
signal expired()

var _target: Node2D
var _velocity: Vector2 = Vector2.RIGHT
var _elapsed: float = 0.0
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)
	_initialized = true


func _physics_process(delta: float) -> void:
	# P8: target pode ter sido removido
	if _target and not is_instance_valid(_target):
		_target = null

	# Steering
	if _target:
		var desired := (_target.global_position - global_position).normalized()
		var angle := _velocity.angle_to(desired)
		var max_turn := turn_rate * delta
		_velocity = _velocity.rotated(clampf(angle, -max_turn, max_turn))

	global_position += _velocity * speed * delta
	rotation = _velocity.angle()

	# Expiração
	if lifetime > 0.0:
		_elapsed += delta
		if _elapsed >= lifetime:
			_expire()


func set_target(target: Node2D) -> void:
	_target = target


func _on_body_entered(body: Node2D) -> void: _handle_hit(body)
func _on_area_entered(area: Area2D) -> void: _handle_hit(area)


func _handle_hit(target: Node) -> void:
	var h := _find_health(target)
	var dmg := 0
	if h and is_instance_valid(h):
		dmg = h.take_damage(damage)
	hit.emit(target, dmg)
	queue_free()


func _find_health(node: Node) -> Health:
	if node is Health: return node
	for c in node.get_children():
		var f := _find_health(c)
		if f: return f
	return null


func _expire() -> void:
	expired.emit()
	queue_free()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if lifetime <= 0.0:
		w.append("lifetime é 0 — projétil nunca expira.")
	return w
