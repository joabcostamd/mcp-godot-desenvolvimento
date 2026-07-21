@tool
class_name Shop
extends Node
@export var shop_name: String = "Loja"
@export var discount: float = 0.0: set(v): discount=clampf(v,0,1)
signal item_bought(item_id: String)
signal item_sold(item_id: String)
signal insufficient_funds()

var _items: Array[Dictionary] = []
var _inventory: Inventory = null
var _currency: Currency = null
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	var p:=get_parent(); if not p: return
	for c in p.get_children():
		if c is Inventory and not _inventory: _inventory=c
		if c is Currency and not _currency: _currency=c
	_initialized=true

func add_item(item_id: String, price: int, quantity: int = -1, buy_price: int = 0) -> void:
	_items.append({"id":item_id,"price":price,"quantity":quantity,"buy_price":buy_price if buy_price>0 else int(price*0.5)})

func buy(item_id: String, quantity: int = 1) -> bool:
	var item:=_find_item(item_id); if item.is_empty(): return false
	if item.quantity>0 and item.quantity<quantity: return false
	var total:=int(item.price*quantity*(1.0-discount))
	if _currency and not _currency.can_afford(total): insufficient_funds.emit(); return false
	if _inventory: _inventory.add_item(item_id,quantity)
	if _currency: _currency.spend(total)
	if item.quantity>0: item.quantity-=quantity
	item_bought.emit(item_id); return true

func sell(item_id: String, quantity: int = 1) -> bool:
	var item:=_find_item(item_id); if item.is_empty(): return false
	var total:=int(item.buy_price*quantity)
	if not _inventory or _inventory.get_item_count(item_id)<quantity: return false
	_inventory.remove_item(item_id,quantity)
	if _currency: _currency.add(total)
	item_sold.emit(item_id); return true

func get_items() -> Array: return _items.duplicate(true)
func _find_item(id: String) -> Dictionary:
	for item in _items:
		if item.id==id: return item
	return {}


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if _items.is_empty():
		w.append("No items added to shop — use add_item() to populate.")
	var p := get_parent()
	if p:
		var has_currency := false
		for c in p.get_children():
			if c is Currency: has_currency = true
		if not has_currency:
			w.append("No Currency sibling found — buy/sell will fail.")
	return w
