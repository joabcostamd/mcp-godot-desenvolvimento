## SaveLoad — Sistema de Save/Load | Godot 4.7 Style Guide compliant.
##
## Salva/restaura estado de behaviors irmãos via ConfigFile.
## Suporta Inventory, Currency, XPLevel. Múltiplos slots.
##
## @behavior: save_load
## @genres: rpg, roguelike, platformer, topdown_shooter, generic
## @tutorial: behaviors/save_load/README.md

@tool
class_name SaveLoad
extends Node

## Diretório de saves.
@export var save_dir: String = "user://saves/":
	set(v):
		var clean := v.strip_edges()
		if clean.is_empty():
			clean = "user://saves/"
		if not clean.ends_with("/"):
			clean += "/"
		save_dir = clean

## Emitido ao salvar.
signal saved(slot: String)

## Emitido ao carregar.
signal loaded(slot: String)

var _inventory: Inventory = null
var _currency: Currency = null
var _xp_level: XPLevel = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_siblings()
	_initialized = true


func _find_siblings() -> void:
	var parent_node := get_parent()
	if not parent_node:
		return
	for child in parent_node.get_children():
		if child is Inventory and not _inventory:
			_inventory = child as Inventory
		if child is Currency and not _currency:
			_currency = child as Currency
		if child is XPLevel and not _xp_level:
			_xp_level = child as XPLevel


## Salva estado dos irmãos no slot especificado.
func save(slot: String) -> bool:
	if slot.is_empty():
		return false

	var config := ConfigFile.new()

	# Inventory: salvar items como dicionário {item_id: count}
	if _inventory:
		var items := {}
		for s in _inventory.get_slots():
			var slot_dict := s as Dictionary
			var sid := slot_dict.get("id", "") as String
			var qty := slot_dict.get("quantity", 0) as int
			if not sid.is_empty() and qty > 0:
				items[sid] = items.get(sid, 0) + qty
		config.set_value("inventory", "slot_count", _inventory.slot_count)
		config.set_value("inventory", "max_stack", _inventory.max_stack)
		config.set_value("inventory", "items", items)

	# Currency
	if _currency:
		config.set_value("currency", "type", _currency.currency_type)
		config.set_value("currency", "amount", _currency.get_amount())

	# XPLevel
	if _xp_level:
		config.set_value("xp_level", "xp", _xp_level.current_xp)
		config.set_value("xp_level", "level", _xp_level.current_level)
		config.set_value("xp_level", "table", _xp_level.xp_table)

	var dir := DirAccess.open("user://")
	if not dir:
		return false
	if not dir.dir_exists(save_dir.trim_suffix("/")):
		dir.make_dir_recursive(save_dir.trim_suffix("/"))

	var path := save_dir.path_join(slot + ".cfg")
	var err := config.save(path)
	if err != OK:
		return false

	saved.emit(slot)
	return true


## Carrega estado dos irmãos do slot especificado.
func load(slot: String) -> bool:
	if slot.is_empty():
		return false

	var path := save_dir.path_join(slot + ".cfg")
	if not FileAccess.file_exists(path):
		return false

	var config := ConfigFile.new()
	var err := config.load(path)
	if err != OK:
		return false

	# Inventory
	if _inventory and config.has_section("inventory"):
		_inventory.clear()
		_inventory.slot_count = config.get_value("inventory", "slot_count", 20) as int
		_inventory.max_stack = config.get_value("inventory", "max_stack", 99) as int
		var items: Dictionary = config.get_value("inventory", "items", {})
		for item_id in items.keys():
			_inventory.add_item(item_id, items[item_id] as int)

	# Currency
	if _currency and config.has_section("currency"):
		_currency.currency_type = config.get_value("currency", "type", "gold") as String
		_currency.amount = config.get_value("currency", "amount", 0) as int

	# XPLevel
	if _xp_level and config.has_section("xp_level"):
		_xp_level.xp_table = config.get_value("xp_level", "table", [0, 100]) as Array
		_xp_level.current_level = config.get_value("xp_level", "level", 1) as int
		_xp_level.current_xp = config.get_value("xp_level", "xp", 0) as int

	loaded.emit(slot)
	return true


## Verifica se um slot existe.
func has_save(slot: String) -> bool:
	if slot.is_empty():
		return false
	return FileAccess.file_exists(save_dir.path_join(slot + ".cfg"))


## Deleta um slot.
func delete_save(slot: String) -> bool:
	if slot.is_empty():
		return false
	var path := save_dir.path_join(slot + ".cfg")
	if not FileAccess.file_exists(path):
		return false
	return DirAccess.remove_absolute(path) == OK


## Lista slots de save disponíveis.
func get_save_slots() -> Array[String]:
	var slots: Array[String] = []
	var dir := DirAccess.open(save_dir)
	if not dir:
		return slots
	dir.list_dir_begin()
	var file_name := dir.get_next()
	while not file_name.is_empty():
		if file_name.ends_with(".cfg"):
			slots.append(file_name.trim_suffix(".cfg"))
		file_name = dir.get_next()
	dir.list_dir_end()
	return slots


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not _inventory and not _currency and not _xp_level:
		w.append("Nenhum behavior irmão detectado — nada para salvar.")
	return w
