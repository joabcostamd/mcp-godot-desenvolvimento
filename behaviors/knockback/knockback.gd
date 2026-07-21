## Knockback — Impulso de Recuo | Godot 4.7 Style Guide compliant.
##
## Node que aplica impulso ao CharacterBody2D pai.
## Conecte ao sinal hit_dealt do hitbox ou chame apply_knockback().
##
## @behavior: knockback
## @genres: platformer, topdown_shooter, fighting, roguelike, metroidvania,
##          generic
## @tutorial: behaviors/knockback/README.md

@tool
class_name Knockback
extends Node

## Intensidade do impulso (px/s).
@export var force: float = 200.0:
	set(value):
		force = clampf(value, 0.0, 5000.0)

## Cooldown entre knockbacks (s).
@export var duration: float = 0.3:
	set(value):
		duration = clampf(value, 0.01, 5.0)
		if _cooldown_timer:
			_cooldown_timer.wait_time = duration

## Reservado para knockback contínuo (não utilizado na v1.0).
@export var damping: float = 0.0:
	set(value):
		damping = clampf(value, 0.0, 1.0)

## Emitido quando o knockback é aplicado.
signal knocked_back(direction: Vector2)

var _can_knockback: bool = true
var _cooldown_timer: Timer
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_create_timer()
	_initialized = true


func _create_timer() -> void:
	if _cooldown_timer:
		return

	_cooldown_timer = Timer.new()
	_cooldown_timer.name = "KnockbackCooldown"
	_cooldown_timer.wait_time = duration
	_cooldown_timer.one_shot = true
	_cooldown_timer.timeout.connect(_on_cooldown_finished)
	add_child(_cooldown_timer)


## Aplica knockback na direção especificada. Retorna false se em cooldown
## ou se o pai não for CharacterBody2D.
func apply_knockback(direction: Vector2) -> bool:
	if not _can_knockback:
		return false

	if direction == Vector2.ZERO:
		return false

	var parent := get_parent()
	if not parent is CharacterBody2D:
		return false

	_can_knockback = false
	var normalized_dir := direction.normalized()
	parent.velocity += normalized_dir * force
	knocked_back.emit(normalized_dir)

	if _cooldown_timer:
		_cooldown_timer.start()

	return true


## Verifica se pode aplicar knockback.
func is_ready() -> bool:
	return _can_knockback


## Reseta o cooldown, permitindo knockback imediato.
func reset() -> void:
	if _cooldown_timer:
		_cooldown_timer.stop()
	_can_knockback = true


func _on_cooldown_finished() -> void:
	_can_knockback = true


## Auto-documentação no editor.
func _get_configuration_warnings() -> PackedStringArray:
	var warnings: PackedStringArray = []
	var parent := get_parent()
	if parent and not parent is CharacterBody2D:
		warnings.append("Parent não é CharacterBody2D — knockback não terá efeito.")
	if force <= 0.0:
		warnings.append("force é 0 — knockback não aplica impulso.")
	return warnings
