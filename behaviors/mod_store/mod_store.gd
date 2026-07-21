## Behavior mod_store para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: mod_store
@tool class_name ModStore extends Node; signal mod_downloaded(mod_id: String); signal mod_rated(mod_id: String, rating: int)
var _initialized: bool = false; func _ready() -> void: if _initialized: return; _initialized=true
func download(mod_id: String) -> void: mod_downloaded.emit(mod_id)
func rate(mod_id: String, rating: int) -> void: mod_rated.emit(mod_id,clampi(rating,1,5))
func _get_configuration_warnings() -> PackedStringArray: return []