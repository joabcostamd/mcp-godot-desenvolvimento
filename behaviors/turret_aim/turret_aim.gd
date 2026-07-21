## TurretAim — Torre que Mira e Atira | Godot 4.7 Style Guide compliant.
##
## Node2D que rotaciona suavemente para seguir um alvo e dispara
## projéteis via FireRate + Projectile. Base para torres de defesa.
##
## @behavior: turret_aim
## @genres: tower_defense, topdown_shooter, roguelike, generic
## @tutorial: behaviors/turret_aim/README.md

@tool
class_name TurretAim
extends Node2D

## Velocidade de rotação (rad/s).
@export var rotation_speed: float = 3.0:
	set(v):
		rotation_speed = clampf(v, 0.1, 20.0)

## Alcance máximo de detecção (px).
@export var detection_range: float = 400.0:
	set(v):
		detection_range = clampf(v, 50.0, 3000.0)

## Antecipa posição futura do alvo.
@export var predict_movement: bool = false

## Tolerância de mira (graus). Abaixo disso, pode atirar.
@export var aim_tolerance_deg: float = 5.0:
	set(v):
		aim_tolerance_deg = clampf(v, 0.5, 45.0)

## Emitido quando está mirando no alvo.
signal target_locked(target: Node2D)

## Emitido quando o alvo sai do alcance.
signal target_lost()

## Emitido ao disparar um projétil.
signal fired(projectile: Node2D)

var _target: Node2D
var _fire_rate: FireRate
var _was_locked: bool = false


func _ready() -> void:
	_find_fire_rate()


func _physics_process(delta: float) -> void:
	if not is_instance_valid(_target):
		_target = _find_in_group("player")
		if not _target:
			return

	var to_target := _target.global_position - global_position
	var distance := to_target.length()

	if distance > detection_range:
		_lose_target()
		return

	# Rotaciona suavemente em direção ao alvo
	var target_angle := to_target.angle()
	var angle_diff := _shortest_angle(rotation, target_angle)
	var max_rotate := rotation_speed * delta

	if absf(angle_diff) <= max_rotate:
		rotation = target_angle
	else:
		rotation += signf(angle_diff) * max_rotate

	# Verifica se está mirando (dentro da tolerância)
	var aim_rad := deg_to_rad(aim_tolerance_deg)
	if absf(angle_diff) <= aim_rad:
		if not _was_locked:
			_was_locked = true
			target_locked.emit(_target)
		_try_fire()
	else:
		_was_locked = false


func _try_fire() -> void:
	if not _fire_rate:
		return
	if _fire_rate.try_fire():
		_spawn_projectile()


func _spawn_projectile() -> void:
	var proj := Projectile.new()
	proj.global_position = global_position
	proj.set_direction(Vector2.RIGHT.rotated(rotation))
	get_parent().add_child(proj)
	fired.emit(proj)


func _lose_target() -> void:
	_target = null
	if _was_locked:
		_was_locked = false
		target_lost.emit()


func _find_fire_rate() -> void:
	var parent := get_parent()
	if parent:
		for child in parent.get_children():
			if child is FireRate and child != self:
				_fire_rate = child
				return


func _find_in_group(group_name: String) -> Node2D:
	var tree := get_tree()
	if tree:
		var nodes := tree.get_nodes_in_group(group_name)
		if nodes.size() > 0:
			return nodes[0] as Node2D
	return null


func _shortest_angle(from_rad: float, to_rad: float) -> float:
	var diff := fmod(to_rad - from_rad + PI, TAU) - PI
	return diff


## Define o alvo manualmente.
func set_target(node: Node2D) -> void:
	_target = node


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not _fire_rate:
		w.append("Nenhum FireRate sibling encontrado — a torre não disparará.")
	return w
