## Behavior mod_loader para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: mod_loader
@tool class_name ModLoader extends Node
@export var mod_directory: String = "user://mods/"; signal mod_loaded(mod_id: String); signal mod_failed(mod_id: String); signal all_mods_loaded()
var _mods: Dictionary = {}; var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func load_mod(mod_id: String) -> void: _mods[mod_id]=true; mod_loaded.emit(mod_id)
func unload_mod(mod_id: String) -> void: if _mods.has(mod_id): _mods.erase(mod_id)
func get_loaded_mods() -> Array[String]: var k:=[]; for key in _mods: k.append(key); return k
func fail_mod(id:String)->void:mod_failed.emit(id)
func finish_loading()->void:all_mods_loaded.emit()
func _get_configuration_warnings() -> PackedStringArray: return []