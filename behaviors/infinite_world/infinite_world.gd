## Behavior infinite_world para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: infinite_world
@tool class_name InfiniteWorld extends Node
@export var chunk_size: int = 16: set(v)=chunk_size=clampi(v,8,128)
@export var view_distance: int = 3: set(v)=view_distance=clampi(v,1,20)
@export var seed_val: int = -1
signal chunk_loaded(chunk_pos: Vector2i); signal chunk_unloaded(chunk_pos: Vector2i)
var _loaded_chunks: Dictionary = {}; var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func load_chunk(pos: Vector2i) -> void:
	if not _loaded_chunks.has(pos): _loaded_chunks[pos]=true; chunk_loaded.emit(pos)
func unload_chunk(pos: Vector2i) -> void:
	if _loaded_chunks.has(pos): _loaded_chunks.erase(pos); chunk_unloaded.emit(pos)
func is_chunk_loaded(pos: Vector2i) -> bool: return _loaded_chunks.has(pos)
func _get_configuration_warnings() -> PackedStringArray: return []
