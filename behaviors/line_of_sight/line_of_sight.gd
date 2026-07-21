## LineOfSight — Visão em Cone | Godot 4.7 Style Guide compliant.
##
## Area2D com CircleShape2D que detecta alvos dentro de um ângulo
## e alcance. Verifica ângulo via dot product com a facing direction
## do pai (eixo X local). Suporta oclusão opcional via RayCast2D.
##
## @behavior: line_of_sight
## @genres: stealth, topdown_shooter, platformer, roguelike, metroidvania, generic
## @tutorial: behaviors/line_of_sight/README.md

@tool
class_name LineOfSight
extends Area2D

## Ângulo total do cone de visão (graus).
@export var view_angle: float = 90.0:
	set(v):
		view_angle = clampf(v, 1.0, 360.0)

## Alcance máximo da visão (px).
@export var view_range: float = 300.0:
	set(v):
		view_range = clampf(v, 10.0, 3000.0)
		_update_collision_shape()

## Número de raycasts para oclusão (0 = sem oclusão, >0 = raycast único).
@export var ray_count: int = 0:
	set(v):
		ray_count = clampi(v, 0, 10)

## Grupo que este sensor detecta.
@export var target_group: String = "player"

## Emitido quando um alvo entra no cone de visão.
signal target_spotted(target: Node2D)

## Emitido quando um alvo sai do cone de visão.
signal target_lost(target: Node2D)

## Alvos atualmente visíveis.
var _targets: Array[Node2D] = []
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	_update_collision_shape()
	_initialized = true


## Atualiza o CircleShape2D com o raio de visão.
func _update_collision_shape() -> void:
	for child in get_children():
		if child is CollisionShape2D:
			var existing_shape := child.shape
			if existing_shape is CircleShape2D:
				existing_shape.radius = view_range
			return
	# Cria o shape se não existir
	var new_shape := CircleShape2D.new()
	new_shape.radius = view_range
	var collision := CollisionShape2D.new()
	collision.shape = new_shape
	add_child(collision)


func _on_body_entered(body: Node2D) -> void:
	_purge_stale_targets()
	if not _is_valid_target(body):
		return
	if body in _targets:
		return
	if not _is_within_angle(body):
		return
	if ray_count > 0 and not _has_line_of_sight(body):
		return

	_targets.append(body)
	target_spotted.emit(body)


func _on_body_exited(body: Node2D) -> void:
	var idx := _targets.find(body)
	if idx >= 0:
		_targets.remove_at(idx)
		target_lost.emit(body)


## Verifica se o corpo pertence ao grupo alvo.
func _is_valid_target(body: Node2D) -> bool:
	if target_group.is_empty():
		return false
	return body.is_in_group(target_group)


## Verifica se o corpo está dentro do ângulo de visão.
## Usa dot product: cos(angle) = dot(facing, to_target) / (|facing| * |to_target|)
func _is_within_angle(body: Node2D) -> bool:
	var facing := _get_facing_direction()
	if facing == Vector2.ZERO:
		return false

	var to_target := body.global_position - global_position
	if to_target.length() > view_range:
		return false

	var dot := facing.normalized().dot(to_target.normalized())
	var half_angle_rad := deg_to_rad(view_angle / 2.0)
	return dot >= cos(half_angle_rad)


## Retorna a direção que o NPC está "olhando" (eixo X do pai, rotacionável).
func _get_facing_direction() -> Vector2:
	var parent := get_parent()
	if parent is Node2D:
		return Vector2.RIGHT.rotated(parent.global_rotation)
	return Vector2.RIGHT


## Dispara raycast para verificar se há linha de visão desobstruída.
## Exclui o próprio sensor e todos os CollisionObject2D irmãos (NPC).
func _has_line_of_sight(body: Node2D) -> bool:
	var space_state := get_world_2d().direct_space_state
	if not space_state:
		return true  # sem physics space, assume visível

	var exclude_rids: Array = [self.get_rid()] + _get_siblings_rids()
	var query := PhysicsRayQueryParameters2D.create(
		global_position, body.global_position, collision_mask, exclude_rids
	)

	var result := space_state.intersect_ray(query)
	return result.is_empty() or result.get("collider") == body


func _get_siblings_rids() -> Array:
	var rids: Array = []
	var parent := get_parent()
	if parent:
		for child in parent.get_children():
			if child is CollisionObject2D and child != self:
				rids.append(child.get_rid())
	return rids


## Remove referências inválidas do array _targets (nós já liberados).
func _purge_stale_targets() -> void:
	var i := _targets.size() - 1
	while i >= 0:
		if not is_instance_valid(_targets[i]):
			_targets.remove_at(i)
		i -= 1


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if collision_mask == 0:
		w.append("collision_mask é 0 — não detecta nenhum corpo.")
	if target_group.is_empty():
		w.append("target_group está vazio — não detecta nenhum grupo.")
	if not _has_collision_shape():
		w.append("Sem CollisionShape2D — área de detecção não definida.")
	return w


func _has_collision_shape() -> bool:
	for child in get_children():
		if child is CollisionShape2D:
			return true
	return false
