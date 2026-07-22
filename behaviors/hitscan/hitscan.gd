## Hitscan — Tiro Instantâneo | Godot 4.7 Style Guide compliant.
##
## RayCast2D one-shot: chame fire() para um disparo único.
## Dano instantâneo ao primeiro alvo na linha de fogo.
## Componente plugável: instancie como filho de uma arma ou torre.
##
## @behavior: hitscan
## @genres: topdown_shooter, platformer, shooter, roguelike, metroidvania, generic
## @tutorial: behaviors/hitscan/README.md

@tool
class_name Hitscan
extends RayCast2D

## Dano causado ao atingir um alvo.
@export var damage: int = 25:
	set(v):
		damage = clampi(v, 1, 9999)

## Alcance máximo do tiro (px).
@export var max_range: float = 1000.0:
	set(v):
		max_range = clampf(v, 10.0, 3000.0)
		target_position = Vector2(max_range, 0.0)

## Duração do flash visual (s).
@export var flash_duration: float = 0.05:
	set(v):
		flash_duration = clampf(v, 0.01, 0.5)
		if _flash_timer:
			_flash_timer.wait_time = flash_duration

## Cor do flash visual.
@export var beam_color: Color = Color.YELLOW:
	set(v):
		beam_color = v
		if _line:
			_line.default_color = beam_color

## Emitido ao final de fire() — sempre, independente de acerto.
signal fired(target: Node, damage_dealt: int)

## Emitido quando o tiro atinge um alvo (antes de fired).
signal hit(target: Node, damage_dealt: int)

## Linha visual do disparo (flash temporário).
var _line: Line2D

## Timer para esconder o flash visual.
var _flash_timer: Timer
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	# enabled já é true por default — respeitar escolha do usuário
	target_position = Vector2(max_range, 0.0)
	_create_visual()
	_create_flash_timer()
	_initialized = true


## Cria a linha visual. Guard anti-duplicação.
func _create_visual() -> void:
	if _line:
		return
	_line = Line2D.new()
	_line.width = 2.0
	_line.default_color = beam_color
	_line.end_cap_mode = Line2D.LINE_CAP_NONE
	_line.add_point(Vector2.ZERO)
	_line.add_point(Vector2(max_range, 0.0))
	_line.visible = false
	add_child(_line)


## Cria o timer de flash. Guard anti-duplicação.
func _create_flash_timer() -> void:
	if _flash_timer:
		return
	_flash_timer = Timer.new()
	_flash_timer.wait_time = flash_duration
	_flash_timer.one_shot = true
	_flash_timer.timeout.connect(_on_flash_timeout)
	add_child(_flash_timer)


## Executa um disparo único. Força raycast update (one-shot),
## aplica dano se houver colisão, emite sinais, mostra flash.
func fire() -> void:
	if not enabled:
		return

	# One-shot: força atualização do raycast neste exato momento
	force_raycast_update()

	if is_colliding():
		var target: Object = get_collider()
		if is_instance_valid(target):
			var h := _find_health(target)
			var damage_dealt := 0
			if h and is_instance_valid(h):
				damage_dealt = h.take_damage(damage)
			hit.emit(target, damage_dealt)
			fired.emit(target, damage_dealt)
		else:
			# P8: target queue_free'd — trata como erro
			fired.emit(null, 0)
	else:
		fired.emit(null, 0)

	# Flash visual
	_show_flash()


## Mostra o flash visual e inicia o timer de auto-hide.
func _show_flash() -> void:
	if not _line:
		return
	# Atualiza ponta da linha: até o ponto de colisão ou max_range
	if is_colliding():
		var collision_local := to_local(get_collision_point())
		_line.set_point_position(1, collision_local)
	else:
		_line.set_point_position(1, Vector2(max_range, 0.0))
	_line.visible = true
	if _flash_timer:
		_flash_timer.start()


func _on_flash_timeout() -> void:
	if _line:
		_line.visible = false


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
		w.append("enabled está false — fire() não terá efeito.")
	if collision_mask == 0:
		w.append("collision_mask é 0 — o tiro não detecta nenhum layer de colisão.")
	return w
