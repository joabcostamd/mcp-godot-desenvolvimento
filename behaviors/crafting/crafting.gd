@tool
class_name Crafting
extends Node
signal crafted(recipe_id: String)
signal missing_ingredients(recipe_id: String)
signal recipe_unlocked(recipe_id: String)

var _recipes: Dictionary = {}
var _unlocked: Array[String] = []
var _inventory: Inventory = null
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	var p:=get_parent(); if not p: return
	for c in p.get_children():
		if c is Inventory and not _inventory: _inventory=c
	_initialized=true

func add_recipe(id: String, output: String, output_qty: int, ingredients: Dictionary, unlocked: bool = true) -> void:
	_recipes[id]={"output":output,"output_qty":output_qty,"ingredients":ingredients}
	if unlocked: _unlocked.append(id); recipe_unlocked.emit(id)

func craft(recipe_id: String) -> bool:
	if recipe_id not in _unlocked: return false
	var r:=_recipes.get(recipe_id,{}); if r.is_empty(): return false
	if not _inventory: return false
	for ing in r.ingredients.keys():
		if _inventory.get_item_count(ing)<r.ingredients[ing]:
			missing_ingredients.emit(recipe_id); return false
	for ing in r.ingredients.keys(): _inventory.remove_item(ing,r.ingredients[ing])
	_inventory.add_item(r.output,r.output_qty)
	crafted.emit(recipe_id); return true

func can_craft(recipe_id: String) -> bool:
	if recipe_id not in _unlocked or not _inventory: return false
	var r:=_recipes.get(recipe_id,{}); if r.is_empty(): return false
	for ing in r.ingredients.keys():
		if _inventory.get_item_count(ing)<r.ingredients[ing]: return false
	return true

func unlock_recipe(id: String) -> void:
	if id in _recipes and id not in _unlocked: _unlocked.append(id); recipe_unlocked.emit(id)
func get_recipes() -> Dictionary: return _recipes.duplicate()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if _recipes.is_empty():
		w.append("No recipes defined — use add_recipe() to add crafting options.")
	if _unlocked.is_empty() and not _recipes.is_empty():
		w.append("Recipes exist but none are unlocked — use unlock_recipe().")
	return w
