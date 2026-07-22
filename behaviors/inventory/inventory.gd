## Inventory — Sistema de Inventário | Godot 4.7 Style Guide compliant.
##
## Sistema de inventário baseado em slots: adiciona, remove e consulta itens.
## Cada slot tem um stack máximo configurável. Emite sinais de item_added,
## item_removed e inventory_full. Plugável em qualquer nó.
##
## @behavior: inventory
## @genres: platformer, topdown_shooter, rpg, roguelike, tower_defense, metroidvania, generic
## @tutorial: behaviors/inventory/README.md

@tool
class_name Inventory
extends Node

## Número total de slots do inventário.
@export var slot_count: int = 20:
	set(v):
		slot_count = clampi(v, 1, 999)
		if _slots.size() != slot_count:
			_resize_slots()

## Quantidade máxima de itens por slot.
@export var max_stack: int = 99:
	set(v):
		max_stack = clampi(v, 1, 999)

## Emitido quando um item é adicionado.
signal item_added(item_id: String, quantity: int, slot: int)

## Emitido quando um item é removido.
signal item_removed(item_id: String, quantity: int, slot: int)

## Emitido quando uma tentativa de adicionar item falha por falta de espaço.
signal inventory_full()

## Estrutura: Array[Dictionary] — cada elemento é {id: String, quantity: int}
var _slots: Array[Dictionary] = []
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	if _slots.is_empty():
		_resize_slots()
	_initialized = true


func _resize_slots() -> void:
	var old_size := _slots.size()
	var new_size := slot_count
	if new_size > old_size:
		for _i in range(new_size - old_size):
			_slots.append({"id": "", "quantity": 0})
	elif new_size < old_size:
		# Emitir item_removed para slots que serao truncados e contem itens
		for i in range(new_size, old_size):
			var removed_slot := _slots[i]
			if removed_slot.id != "" and removed_slot.quantity > 0:
				item_removed.emit(removed_slot.id, removed_slot.quantity, i)
		_slots.resize(new_size)


## Adiciona itens ao inventário.
## Retorna a quantidade efetivamente adicionada (0 = inventário cheio).
## Preenche slots existentes do mesmo ID primeiro, depois abre novos slots.
func add_item(item_id: String, quantity: int) -> int:
	if quantity <= 0 or item_id.is_empty():
		return 0

	var remaining := quantity
	var added := 0

	# 1. Preencher slots existentes do mesmo ID
	for i in _slots.size():
		if remaining <= 0:
			break
		var existing := _slots[i]
		if existing.id == item_id and existing.quantity < max_stack:
			var space := max_stack - existing.quantity
			var fill := mini(remaining, space)
			_set_slot(i, item_id, existing.quantity + fill)
			remaining -= fill
			added += fill

	# 2. Preencher slots vazios
	for i in _slots.size():
		if remaining <= 0:
			break
		var empty_slot := _slots[i]
		if empty_slot.id == "" or empty_slot.quantity == 0:
			var can_fill := mini(remaining, max_stack)
			_set_slot(i, item_id, can_fill)
			remaining -= can_fill
			added += can_fill

	if remaining > 0:
		inventory_full.emit()

	return added


## Remove itens do inventário.
## Retorna a quantidade efetivamente removida (0 = item não encontrado).
## Remove de slots parcialmente preenchidos primeiro (ordem reversa).
func remove_item(item_id: String, quantity: int) -> int:
	if quantity <= 0 or item_id.is_empty():
		return 0

	var remaining := quantity
	var removed := 0

	# Remove do último slot para o primeiro (para esvaziar slots parciais primeiro)
	for i in range(_slots.size() - 1, -1, -1):
		if remaining <= 0:
			break
		var slot := _slots[i]
		if slot.id == item_id and slot.quantity > 0:
			var to_remove := mini(remaining, slot.quantity)
			var new_qty := slot.quantity - to_remove
			if new_qty <= 0:
				_set_slot(i, "", 0)
			else:
				_set_slot(i, item_id, new_qty)
			remaining -= to_remove
			removed += to_remove

	return removed


## Verifica se o inventário possui pelo menos a quantidade especificada do item.
## Retorna false para quantity <= 0 ou item_id vazio.
func has_item(item_id: String, quantity: int = 1) -> bool:
	if quantity <= 0 or item_id.is_empty():
		return false
	return get_item_count(item_id) >= quantity


## Retorna a quantidade total de um item em todos os slots.
func get_item_count(item_id: String) -> int:
	var total := 0
	for slot in _slots:
		if slot.id == item_id:
			total += slot.quantity
	return total


## Retorna o índice do primeiro slot livre (-1 se cheio).
func get_free_slot() -> int:
	for i in _slots.size():
		var slot := _slots[i]
		if slot.id == "" or slot.quantity == 0:
			return i
	return -1


## Retorna true se todos os slots estão ocupados.
func is_full() -> bool:
	return get_free_slot() == -1


## Esvazia completamente o inventário.
func clear() -> void:
	for i in _slots.size():
		if _slots[i].id != "":
			_set_slot(i, "", 0)


## Retorna uma cópia dos slots (para debug/UI).
func get_slots() -> Array[Dictionary]:
	return _slots.duplicate(true)


## Setter centralizado de slot. Único ponto que modifica _slots.
## Emite item_removed se ID mudou ou quantidade diminuiu.
## Emite item_added se ID mudou ou quantidade aumentou.
## Se mesmo ID com quantidade diferente, emite net change.
func _set_slot(index: int, item_id: String, quantity: int) -> void:
	if index < 0 or index >= _slots.size():
		return

	var old := _slots[index]
	if old.id == item_id and old.quantity == quantity:
		return  # no-op

	var old_id := old.id
	var old_qty := old.quantity

	_slots[index] = {"id": item_id, "quantity": quantity}

	# Mesmo item — emitir delta, nao remove+add separados
	if old_id == item_id and old_id != "":
		var delta := quantity - old_qty
		if delta > 0:
			item_added.emit(item_id, delta, index)
		elif delta < 0:
			item_removed.emit(item_id, -delta, index)
		return

	# Item diferente — remover antigo e adicionar novo
	if old_id != "" and old_qty > 0:
		item_removed.emit(old_id, old_qty, index)
	if item_id != "" and quantity > 0:
		item_added.emit(item_id, quantity, index)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	# Avisar sobre slot_count == 1 (slot unico — utilizavel mas limitado)
	if slot_count == 1:
		w.append("Apenas 1 slot disponivel — inventario extremamente limitado.")
	return w
