## StatusEffect — Efeito de Status (Buff/Debuff) | Godot 4.7.
##
## Node que aplica um efeito temporário a uma entidade.
## Suporta dano/cura por tick (DoT/HoT), stacks acumuláveis,
## refresh de duração e remoção manual.
## Auto-detecta Health sibling para aplicar dano/cura.
##
## @behavior: status_effect
## @genres: rpg, roguelike, platformer, topdown_shooter, generic
## @tutorial: behaviors/status_effect/README.md

@tool
class_name StatusEffect
extends Node

## Tipo do efeito (ex: "burn", "poison", "freeze", "haste", "shield").
@export var effect_type: String = "custom"

## Duração total (0 = permanente até remove()).
@export var duration: float = 5.0:
	set(v):
		duration = clampf(v, 0.0, 300.0)

## Intervalo entre ticks (0 = sem ticks).
@export var tick_interval: float = 1.0:
	set(v):
		tick_interval = clampf(v, 0.0, 10.0)

## Dano por tick (positivo = dano, negativo = cura). 0 = sem efeito.
@export var tick_damage: int = 0

## Número máximo de stacks acumuláveis.
@export var max_stacks: int = 1:
	set(v):
		max_stacks = clampi(v, 1, 99)

signal applied()
signal tick(stacks: int)
signal expired()
signal refreshed()
signal removed()

var _stacks: int = 0
var _elapsed: float = 0.0
var _tick_elapsed: float = 0.0
var _active: bool = false
var _health: Health = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_health()
	_initialized = true


func _find_health() -> void:
	var parent := get_parent()
	if not parent:
		return
	for child in parent.get_children():
		if child is Health:
			_health = child as Health
			return


func _process(delta: float) -> void:
	if not _active:
		return

	_elapsed += delta

	# Tick
	if tick_interval > 0.0 and tick_damage != 0:
		_tick_elapsed += delta
		if _tick_elapsed >= tick_interval:
			_tick_elapsed = fmod(_tick_elapsed, tick_interval)
			_apply_tick()

	# Expiração
	if duration > 0.0 and _elapsed >= duration:
		_active = false
		expired.emit()


func _apply_tick() -> void:
	if not _health:
		return

	var total_damage := tick_damage * _stacks
	if total_damage > 0:
		_health.take_damage(total_damage, effect_type)
	elif total_damage < 0:
		_health.heal(-total_damage)

	tick.emit(_stacks)


## Aplica o efeito (ou adiciona stack se já ativo).
func apply() -> void:
	if _stacks >= max_stacks:
		refresh()
		return

	_stacks += 1
	if not _active:
		_active = true
		_elapsed = 0.0
		_tick_elapsed = 0.0
		applied.emit()


## Renova a duração do efeito (mantém stacks).
func refresh() -> void:
	_elapsed = 0.0
	refreshed.emit()


## Remove o efeito manualmente.
func remove() -> void:
	_active = false
	removed.emit()


## Retorna true se o efeito está ativo.
func is_active() -> bool:
	return _active


## Retorna o número atual de stacks.
func get_stacks() -> int:
	return _stacks


## Retorna a duração restante (0 se permanente).
func get_remaining_time() -> float:
	if duration <= 0.0:
		return -1.0  # permanente
	return maxf(0.0, duration - _elapsed)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if tick_interval > 0.0 and tick_damage == 0:
		w.append("tick_interval is set but tick_damage is 0 — ticks will have no effect.")
	if not _health:
		w.append("No Health sibling found — tick damage/healing will not be applied.")
	if effect_type == "custom":
		w.append("effect_type is 'custom' — consider setting a meaningful type for game logic.")
	return w
