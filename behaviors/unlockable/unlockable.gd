## Unlockable — Metaprogression | Godot 4.7 Style Guide compliant.
##
## Desbloqueia conteúdo baseado em condições. Auto-detecta
## Achievement, XPLevel, Currency irmãos.
##
## @behavior: unlockable
## @genres: roguelike, rpg, platformer, generic
## @tutorial: behaviors/unlockable/README.md

@tool
class_name Unlockable
extends Node

## Lista: [{id, name, conditions: [{type, target_id, required}]}]
@export var unlocks: Array = []

signal unlocked(unlock_id: String)

var _achievement: Achievement = null
var _xp_level: XPLevel = null
var _currency: Currency = null
var _unlocked: Array[String] = []
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_find_siblings()
	_check_all_unlocks()
	_initialized = true


func _find_siblings() -> void:
	var p := get_parent()
	if not p: return
	for c in p.get_children():
		if c is Achievement and not _achievement:
			_achievement = c; _achievement.unlocked.connect(_on_achievement_unlocked)
		if c is XPLevel and not _xp_level:
			_xp_level = c; _xp_level.leveled_up.connect(_on_level_up)
		if c is Currency and not _currency:
			_currency = c; _currency.gained.connect(_on_currency_changed)


func _on_achievement_unlocked(_id: String) -> void:
	_check_all_unlocks()


func _on_level_up(_level: int) -> void:
	_check_all_unlocks()


func _on_currency_changed(_v: int, _t: int) -> void:
	_check_all_unlocks()


func _check_all_unlocks() -> void:
	for u in unlocks:
		var ud := u as Dictionary
		var uid := ud.get("id", "") as String
		if uid in _unlocked: continue
		if _check_conditions(ud.get("conditions", []) as Array):
			_unlocked.append(uid)
			unlocked.emit(uid)


func _check_conditions(conditions: Array) -> bool:
	for c in conditions:
		var cd := c as Dictionary
		var ctype := cd.get("type", "") as String
		var target := cd.get("target_id", "") as String
		var req := cd.get("required", 1) as int

		match ctype:
			"achievement":
				if not _achievement or not _achievement.is_unlocked(target):
					return false
			"level":
				if not _xp_level or _xp_level.current_level < req:
					return false
			"currency":
				if not _currency or _currency.get_amount() < req:
					return false
			_:
				return false
	return true


func is_unlocked(unlock_id: String) -> bool:
	return unlock_id in _unlocked


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if unlocks.is_empty():
		w.append("unlocks está vazio — nenhum desbloqueio definido.")
	return w
