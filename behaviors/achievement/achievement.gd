## Achievement — Sistema de Conquistas | Godot 4.7 Style Guide compliant.
##
## Rastreia condições (collect, currency, level) e desbloqueia conquistas.
## Auto-detecta Inventory, Currency, XPLevel irmãos.
##
## @behavior: achievement
## @genres: platformer, topdown_shooter, rpg, roguelike, generic
## @tutorial: behaviors/achievement/README.md

@tool
class_name Achievement
extends Node

## Lista: [{id, name, condition: {type, target_id, required}}]
@export var achievements: Array = []

signal unlocked(achievement_id: String)
signal progress_updated(achievement_id: String, current: int, required: int)

var _inventory: Inventory = null
var _currency: Currency = null
var _xp_level: XPLevel = null
var _progress: Dictionary = {}  # id → current
var _unlocked: Array[String] = []
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_siblings()
	_initialized = true


func _find_siblings() -> void:
	var p := get_parent()
	if not p: return
	for c in p.get_children():
		if c is Inventory and not _inventory:
			_inventory = c; _inventory.item_added.connect(_on_item_added)
		if c is Currency and not _currency:
			_currency = c; _currency.gained.connect(_on_currency_changed)
		if c is XPLevel and not _xp_level:
			_xp_level = c; _xp_level.leveled_up.connect(_on_level_up)


func _on_item_added(item_id: String, _qty: int, _slot: int) -> void:
	for ach in achievements:
		var a := ach as Dictionary
		var cond := a.get("condition", {}) as Dictionary
		if cond.get("type", "") == "collect" and cond.get("target_id", "") == item_id:
			_update_progress(a.id, _inventory.get_item_count(item_id), cond.required)


func _on_currency_changed(_value: int, _total: int) -> void:
	if not _currency: return
	for ach in achievements:
		var a := ach as Dictionary
		var cond := a.get("condition", {}) as Dictionary
		if cond.get("type", "") == "currency":
			_update_progress(a.id, _currency.get_amount(), cond.required)


func _on_level_up(new_level: int) -> void:
	for ach in achievements:
		var a := ach as Dictionary
		var cond := a.get("condition", {}) as Dictionary
		if cond.get("type", "") == "level":
			_update_progress(a.id, new_level, cond.required)


func _update_progress(ach_id: String, current: int, required: int) -> void:
	var clamped := mini(current, required)
	if ach_id in _unlocked:
		return
	_progress[ach_id] = clamped
	progress_updated.emit(ach_id, clamped, required)
	if clamped >= required:
		_unlocked.append(ach_id)
		unlocked.emit(ach_id)


func get_progress(ach_id: String) -> Dictionary:
	return {"current": _progress.get(ach_id, 0), "required": _get_required(ach_id)}


func is_unlocked(ach_id: String) -> bool:
	return ach_id in _unlocked


func _get_required(ach_id: String) -> int:
	for ach in achievements:
		var a := ach as Dictionary
		if a.get("id", "") == ach_id:
			return (a.get("condition", {}) as Dictionary).get("required", 0)
	return 0


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if achievements.is_empty():
		w.append("achievements está vazio — nenhuma conquista definida.")
	return w
