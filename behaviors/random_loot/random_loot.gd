@tool class_name RandomLoot extends Node
@export var loot_table: Array = []
signal loot_dropped(item_id: String)
signal rare_drop(item_id: String)
var _inventory: Inventory = null
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	_find_inventory(); _initialized=true
func _find_inventory() -> void:
	var p:=get_parent(); if not p: return
	for c in p.get_children():
		if c is Inventory: _inventory=c as Inventory; return
func roll() -> String:
	if loot_table.is_empty(): return ""
	var total:=0.0
	for e in loot_table: total+=(e as Dictionary).get("weight",1.0)
	var r:=randf()*total; var acc:=0.0
	for e in loot_table:
		var d:=e as Dictionary; acc+=d.get("weight",1.0)
		if r<=acc:
			var id:=d.get("id","") as String
			loot_dropped.emit(id)
			if d.get("rarity","common") in ["rare","epic","legendary"]: rare_drop.emit(id)
			if _inventory: _inventory.add_item(id,1)
			return id
	return ""
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if loot_table.is_empty(): w.append("loot_table vazia — roll() sempre retorna ''.")
	return w
