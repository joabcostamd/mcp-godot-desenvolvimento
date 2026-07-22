## EquipmentSlot — Slot de Equipamento | Godot 4.7.
##
## Node que gerencia um slot de equipamento com tipo e bônus.
## Integra com Inventory (para itens) e CharacterStats (para bônus).
##
## @behavior: equipment_slot
## @genres: rpg, roguelike, generic
## @tutorial: behaviors/equipment_slot/README.md

@tool
class_name EquipmentSlot
extends Node

@export var slot_type: String = "weapon"
@export var slot_bonus: float = 1.0:
	set(v):
		slot_bonus = clampf(v, 0.0, 5.0)

signal equipped(item_id: String)
signal unequipped(item_id: String)

var _equipped_item: String = ""
var _item_stats: Dictionary = {}
var _inventory: Inventory = null
var _stats: CharacterStats = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_dependencies()
	_initialized = true


func _find_dependencies() -> void:
	var parent := get_parent()
	if not parent:
		return
	for child in parent.get_children():
		if child is Inventory and not _inventory:
			_inventory = child as Inventory
		if child is CharacterStats and not _stats:
			_stats = child as CharacterStats


## Equipa um item do inventário neste slot.
## Retorna true se equipado com sucesso.
func equip(item_id: String) -> bool:
	if not _inventory:
		return false
	if _inventory.get_item_count(item_id) < 1:
		return false

	# Desequipa item atual se houver
	if not _equipped_item.is_empty():
		unequip()

	# Remove do inventário e equipa
	_inventory.remove_item(item_id, 1)
	_equipped_item = item_id
	_item_stats = _get_item_stats(item_id)
	_apply_bonus()

	equipped.emit(item_id)
	return true


## Desequipa o item atual e o devolve ao inventário.
func unequip() -> void:
	if _equipped_item.is_empty():
		return

	var old_item := _equipped_item
	_remove_bonus()
	if _inventory:
		_inventory.add_item(old_item, 1)
	_equipped_item = ""
	_item_stats.clear()

	unequipped.emit(old_item)


## Retorna o ID do item equipado (vazio se nenhum).
func get_equipped_item() -> String:
	return _equipped_item


## Retorna true se há um item equipado.
func has_equipped() -> bool:
	return not _equipped_item.is_empty()


func _get_item_stats(item_id: String) -> Dictionary:
	# Stats típicos de item: {"strength": 5, "intelligence": 3}
	# Na prática, viriam de um Resource ou data table
	return {"strength": 2, "dexterity": 1, "intelligence": 0, "vitality": 0}


func _apply_bonus() -> void:
	if not _stats:
		return
	for stat in _item_stats.keys():
		var value: float = _item_stats[stat] * slot_bonus
		if value > 0:
			_stats.add_modifier(stat, 1.0 + value * 0.01)


func _remove_bonus() -> void:
	if not _stats:
		return
	for stat in _item_stats.keys():
		_stats.clear_modifiers(stat)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not _inventory:
		w.append("No Inventory sibling found — cannot equip items.")
	if not _stats:
		w.append("No CharacterStats sibling found — bonuses will not be applied.")
	if slot_type.is_empty():
		w.append("slot_type is empty — consider setting a type like 'weapon' or 'armor'.")
	return w
