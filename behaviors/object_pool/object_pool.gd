## ObjectPool — Pool de Objetos | Godot 4.7.
##
## Pré-instancia pool_size cópias de um PackedScene. Gerencia
## take() e return_object(). Expansível se expandable=true.
##
## @behavior: object_pool
## @genres: generic
## @tutorial: behaviors/object_pool/README.md

@tool
class_name ObjectPool
extends Node

@export var pool_size: int = 20:
	set(v): pool_size = clampi(v, 1, 1000)
@export var prefab: PackedScene
@export var expandable: bool = true

signal object_taken(obj: Node)
signal object_returned(obj: Node)
signal pool_empty()

var _available: Array[Node] = []
var _active: Array[Node] = []
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	if not prefab:
		return
	for i in range(pool_size):
		_create_and_pool()
	_initialized = true


func _create_and_pool() -> void:
	var obj := prefab.instantiate()
	_deactivate(obj)
	add_child(obj)
	_available.append(obj)


func take() -> Node:
	_purge_stale()
	if _available.is_empty():
		if expandable and prefab:
			_create_and_pool()
		else:
			pool_empty.emit()
			return null

	var obj := _available.pop_back()
	_activate(obj)
	_active.append(obj)
	object_taken.emit(obj)
	return obj


func return_object(obj: Node) -> void:
	var idx := _active.find(obj)
	if idx < 0:
		return
	_active.remove_at(idx)
	_deactivate(obj)
	_available.append(obj)
	object_returned.emit(obj)


func _activate(obj: Node) -> void:
	obj.process_mode = Node.PROCESS_MODE_INHERIT
	if obj is CanvasItem:
		(obj as CanvasItem).visible = true


func _deactivate(obj: Node) -> void:
	obj.process_mode = Node.PROCESS_MODE_DISABLED
	if obj is CanvasItem:
		(obj as CanvasItem).visible = false


func _purge_stale() -> void:
	var i := _active.size() - 1
	while i >= 0:
		if not is_instance_valid(_active[i]):
			_active.remove_at(i)
		i -= 1


func get_available_count() -> int:
	return _available.size()


func get_active_count() -> int:
	return _active.size()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not prefab:
		w.append("prefab não definido — o pool não criará objetos.")
	if not expandable:
		w.append("expandable=false — o pool não criará novos objetos quando esgotar.")
	return w
