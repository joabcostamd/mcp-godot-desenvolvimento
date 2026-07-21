## BeamLaser — Raio Contínuo Instantâneo | Godot 4.7 Style Guide compliant.
##
## RayCast2D que causa dano por segundo enquanto o raio atinge um alvo.
## Componente plugável: instancie como filho de uma arma, torre ou inimigo.
##
## @behavior: beam_laser
## @genres: topdown_shooter, platformer, bullet_hell, tower_defense,
##          metroidvania, generic
## @tutorial: behaviors/beam_laser/README.md

@tool
class_name BeamLaser
extends RayCast2D

## Dano causado por segundo enquanto o raio atinge (dps).
@export var damage_per_second: float = 30.0:
	set(v):
		damage_per_second = clampf(v, 1.0, 9999.0)

## Largura visual do raio (px).
@export var beam_width: float = 4.0:
	set(v):
		beam_width = clampf(v, 1.0, 50.0)
		if _line:
			_line.width = beam_width

## Alcance máximo do raio (px).
@export var max_range: float = 500.0:
	set(v):
		max_range = clampf(v, 10.0, 2000.0)
		target_position = Vector2(max_range, 0.0)

## Cor do raio visual.
@export var beam_color: Color = Color.RED:
	set(v):
		beam_color = v
		if _line:
			_line.default_color = beam_color

## Emitido a cada frame de física enquanto o raio atinge algo.
signal hitting(target: Node, dps: float)

## Emitido quando o raio para de atingir (transição hit→no-hit).
signal stopped()

## Acumulador de dano (aplica em chunks inteiros para evitar spam de take_damage).
var _damage_accumulator: float = 0.0

## Se estava atingindo no frame anterior (para detectar transição).
var _was_hitting: bool = false

## Linha visual do raio.
var _line: Line2D


func _ready() -> void:
	# enabled já é true por default no RayCast2D — respeitar escolha do usuário
	target_position = Vector2(max_range, 0.0)
	_create_visual()


## Cria a linha visual do raio. Guard anti-duplicação.
func _create_visual() -> void:
	if _line:
		return
	_line = Line2D.new()
	_line.width = beam_width
	_line.default_color = beam_color
	_line.end_cap_mode = Line2D.LINE_CAP_NONE
	_line.add_point(Vector2.ZERO)
	_line.add_point(Vector2(max_range, 0.0))
	add_child(_line)


func _physics_process(delta: float) -> void:
	# Respeitar enabled: se desligado, não processa (nem visual)
	if not enabled:
		return

	# RayCast2D já é atualizado automaticamente a cada frame de física.
	# NÃO chamar force_raycast_update() aqui — respeita o ciclo natural
	# e evita que o beam funcione mesmo com enabled=false.

	if is_colliding():
		var target: Object = get_collider()
		# P8: target pode ter sido queue_free'd entre o raycast e este frame
		if not is_instance_valid(target):
			_hit_to_no_hit()
			return

		# Acumula dano e aplica em chunks inteiros
		_damage_accumulator += damage_per_second * delta
		var damage_to_apply := int(_damage_accumulator)
		if damage_to_apply > 0:
			var h := _find_health(target)
			if h and is_instance_valid(h):
				h.take_damage(damage_to_apply)
			_damage_accumulator -= float(damage_to_apply)

		hitting.emit(target, damage_per_second)

		if not _was_hitting:
			_was_hitting = true

		# Atualiza visual: linha da origem ao ponto de colisão
		var collision_local := to_local(get_collision_point())
		_update_line(collision_local)
	else:
		_hit_to_no_hit()
		# Visual: linha até max_range
		_update_line(Vector2(max_range, 0.0))


func _hit_to_no_hit() -> void:
	if _was_hitting:
		_was_hitting = false
		_damage_accumulator = 0.0
		stopped.emit()


## Atualiza a ponta da linha visual. Usa set_point_position porque
## Line2D.points retorna cópia (PackedVector2Array) — atribuição
## direta por índice não teria efeito.
func _update_line(end_point: Vector2) -> void:
	if _line:
		_line.set_point_position(1, end_point)


## Procura por um componente Health no nó alvo ou nos filhos.
func _find_health(node: Object) -> Health:
	if node is Health:
		return node
	if node is Node:
		var n: Node = node as Node
		for child in n.get_children():
			if child is Health:
				return child
	return null


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not enabled:
		w.append("enabled está false — o raio não causará dano nem será visível.")
	if collision_mask == 0:
		w.append("collision_mask é 0 — o raio não detecta nenhum layer de colisão.")
	return w
