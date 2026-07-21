## AreaDamage — Dano em Área | Godot 4.7 Style Guide compliant.
##
## Area2D que causa dano explosivo a todos os Health no raio.
## Chame explode() para ativar. One-shot — não é campo persistente.
##
## @behavior: area_damage
## @genres: topdown_shooter, platformer, roguelike, bullet_hell, generic
## @tutorial: behaviors/area_damage/README.md

@tool
class_name AreaDamage
extends Area2D

## Dano no centro da explosão.
@export var damage: int = 50:
	set(value):
		damage = clampi(value, 1, 9999)

## Raio da explosão (px).
@export var radius: float = 100.0:
	set(value):
		radius = clampf(value, 10.0, 2000.0)
		_update_shape()

## Falloff: 0.0 = dano total no raio, 1.0 = zero na borda.
@export var falloff: float = 0.5:
	set(value):
		falloff = clampf(value, 0.0, 1.0)

## Força de knockback (0 = sem).
@export var explosion_force: float = 300.0:
	set(value):
		explosion_force = clampf(value, 0.0, 5000.0)

## Emitido após a explosão.
signal exploded(targets_hit: int)


func _ready() -> void:
	_update_shape()


func _update_shape() -> void:
	for child in get_children():
		if child is CollisionShape2D and child.shape is CircleShape2D:
			(child.shape as CircleShape2D).radius = radius
			break


## Ativa a explosão. Retorna o número de alvos atingidos.
func explode() -> int:
	var targets_hit := 0
	var origin := global_position

	# Corpos (CharacterBody2D, etc.)
	for body in get_overlapping_bodies():
		targets_hit += _apply_to_target(body, origin)

	# Áreas (outras Area2D com Health)
	for area in get_overlapping_areas():
		targets_hit += _apply_to_target(area, origin)

	exploded.emit(targets_hit)
	return targets_hit


func _apply_to_target(target: Node, origin: Vector2) -> int:
	var health := _find_health(target)
	if not health or not is_instance_valid(health):
		return 0

	var target_pos := origin
	if target is Node2D:
		target_pos = (target as Node2D).global_position
	var distance := target_pos.distance_to(origin)
	var t := clampf(distance / maxf(radius, 1.0), 0.0, 1.0)
	var dmg := ceili(damage * (1.0 - t * falloff))

	var dealt := health.take_damage(dmg)
	if dealt <= 0:
		return 0

	# Knockback
	if explosion_force > 0.0:
		_apply_knockback(target, origin)

	return 1


func _apply_knockback(target: Node, origin: Vector2) -> void:
	var kb := _find_knockback(target)
	if not kb:
		return
	var target_pos := origin
	if target is Node2D:
		target_pos = (target as Node2D).global_position
	var dir := (target_pos - origin).normalized()
	kb.apply_knockback(dir)


func _find_health(node: Node) -> Health:
	if node is Health:
		return node
	for child in node.get_children():
		var found := _find_health(child)
		if found:
			return found
	return null


func _find_knockback(node: Node) -> Knockback:
	if node is Knockback:
		return node
	for child in node.get_children():
		var found := _find_knockback(child)
		if found:
			return found
	return null


func _get_configuration_warnings() -> PackedStringArray:
	var warnings: PackedStringArray = []
	var has_shape := false
	for child in get_children():
		if child is CollisionShape2D:
			has_shape = true
			break
	if not has_shape:
		warnings.append("Nenhum CollisionShape2D encontrado — explosão não detectará alvos.")
	return warnings
