## Behavior save_slots para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: save_slots
@tool class_name SaveSlots extends Node
@export var slot_count: int = 3: set(v)=slot_count=clampi(v,1,20)
signal slot_created(slot: int); signal slot_deleted(slot: int)
var _slots: Array[Dictionary] = []
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	for i in slot_count: _slots.append({"name":"Slot "+str(i+1),"empty":true})
	_initialized=true
func get_slot(index: int) -> Dictionary:
	if index<0 or index>=_slots.size(): return {}
	return _slots[index]
func mark_slot_used(index: int) -> void:
	if index>=0 and index<_slots.size(): _slots[index]["empty"]=false; slot_created.emit(index)
func delete_slot(index: int) -> void:
	if index>=0 and index<_slots.size(): _slots[index]["empty"]=true; slot_deleted.emit(index)
func get_empty_slot() -> int:
	for i in _slots.size():
		if _slots[i]["empty"]: return i
	return -1
func _get_configuration_warnings() -> PackedStringArray: return []
