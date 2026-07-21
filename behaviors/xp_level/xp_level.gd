## XPLevel — Sistema de XP e Nível | Godot 4.7 Style Guide compliant.
##
## Gerencia XP e nível com tabela de progressão configurável.
## Ganha XP via add_xp(), sobe de nível automaticamente.
## Suporta múltiplos level ups em uma chamada.
##
## @behavior: xp_level
## @genres: rpg, roguelike, platformer, topdown_shooter, idle, generic
## @tutorial: behaviors/xp_level/README.md

@tool
class_name XPLevel
extends Node

## Thresholds de XP por nível. xp_table[n] = XP para nível n+1.
@export var xp_table: Array[int] = [0, 100, 300, 600]

## XP acumulado atual.
@export var current_xp: int = 0:
	set(v):
		current_xp = clampi(v, 0, 999999)

## Nível atual (mínimo 1).
@export var current_level: int = 1:
	set(v):
		current_level = clampi(v, 1, 999)

## Emitido ao ganhar XP.
signal xp_gained(value: int, total_xp: int)

## Emitido a cada nível ganho.
signal leveled_up(new_level: int)

var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_initialized = true


## Adiciona XP. Retorna o número de níveis ganhos.
## value <= 0 é no-op, retorna 0.
func add_xp(value: int) -> int:
	if value <= 0:
		return 0

	current_xp += value
	xp_gained.emit(value, current_xp)

	var levels_gained := 0
	while current_level < xp_table.size() and current_xp >= xp_table[current_level]:
		current_level += 1
		levels_gained += 1
		leveled_up.emit(current_level)

	return levels_gained


## XP restante para o próximo nível.
## Retorna -1 se estiver no nível máximo.
func get_xp_to_next() -> int:
	if is_max_level():
		return -1
	return maxi(0, xp_table[current_level] - current_xp)


## Nível máximo baseado na tabela.
func get_max_level() -> int:
	return xp_table.size()


## Está no nível máximo?
func is_max_level() -> bool:
	return xp_table.is_empty() or current_level >= xp_table.size()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if xp_table.is_empty():
		w.append("xp_table está vazia — add_xp() será no-op (max level).")
	elif xp_table[0] != 0:
		w.append("xp_table[0] deveria ser 0 (nível 1 não exige XP).")
	return w
