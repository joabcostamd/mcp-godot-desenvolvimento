## CharacterStats — Atributos de Personagem RPG | Godot 4.7.
##
## Node que gerencia atributos base (STR, DEX, INT, VIT).
## Fornece bônus derivados: dano físico, dano mágico,
## velocidade de ataque, HP máximo. Integra com Health sibling.
##
## @behavior: character_stats
## @genres: rpg, roguelike, generic
## @tutorial: behaviors/character_stats/README.md

@tool
class_name CharacterStats
extends Node

@export var strength: int = 10:
	set(v):
		strength = clampi(v, 1, 999)
		stat_changed.emit("strength", strength)
@export var dexterity: int = 10:
	set(v):
		dexterity = clampi(v, 1, 999)
		stat_changed.emit("dexterity", dexterity)
@export var intelligence: int = 10:
	set(v):
		intelligence = clampi(v, 1, 999)
		stat_changed.emit("intelligence", intelligence)
@export var vitality: int = 10:
	set(v):
		vitality = clampi(v, 1, 999)
		stat_changed.emit("vitality", vitality)
		_update_max_hp()

signal stat_changed(stat_name: String, new_value: int)

var _modifiers: Dictionary = {}  # stat_name -> Array[float] (multipliers)
var _health: Health = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_health()
	_update_max_hp()
	_initialized = true


func _find_health() -> void:
	var parent := get_parent()
	if not parent:
		return
	for child in parent.get_children():
		if child is Health:
			_health = child as Health
			return


func _update_max_hp() -> void:
	if not _health:
		return
	var base_hp := vitality * 10
	var modifier := _get_stat_multiplier("vitality")
	_health.max_hp = int(base_hp * modifier)


## Retorna o dano físico base (derivado de strength).
func get_physical_damage() -> int:
	var base := strength * 2
	return int(base * _get_stat_multiplier("strength"))


## Retorna o dano mágico base (derivado de intelligence).
func get_magic_damage() -> int:
	var base := intelligence * 2
	return int(base * _get_stat_multiplier("intelligence"))


## Retorna a velocidade de ataque (derivado de dexterity).
func get_attack_speed() -> float:
	var base := 1.0 + dexterity * 0.02
	return base * _get_stat_multiplier("dexterity")


## Adiciona um modificador multiplicativo temporário a um atributo.
## Ex: add_modifier("strength", 1.5) aumenta dano físico em 50%.
func add_modifier(stat_name: String, multiplier: float) -> void:
	if not _modifiers.has(stat_name):
		_modifiers[stat_name] = []
	_modifiers[stat_name].append(multiplier)


## Remove todos os modificadores de um atributo.
func clear_modifiers(stat_name: String) -> void:
	if _modifiers.has(stat_name):
		_modifiers[stat_name].clear()


func _get_stat_multiplier(stat_name: String) -> float:
	if not _modifiers.has(stat_name):
		return 1.0
	var modifiers: Array = _modifiers[stat_name]
	var result := 1.0
	for m in modifiers:
		result *= m
	return result


## Retorna o valor de um atributo (considerando modificadores).
func get_stat(stat_name: String) -> int:
	match stat_name:
		"strength": return int(strength * _get_stat_multiplier("strength"))
		"dexterity": return int(dexterity * _get_stat_multiplier("dexterity"))
		"intelligence": return int(intelligence * _get_stat_multiplier("intelligence"))
		"vitality": return int(vitality * _get_stat_multiplier("vitality"))
	return 0


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not _health:
		w.append("No Health sibling found — vitality won't affect max_hp.")
	return w
