## Behavior mod_config para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: mod_config
@tool class_name ModConfig extends Node; signal config_validated(mod_id: String); signal conflict_detected(mod_a: String, mod_b: String)
var _initialized: bool = false; func _ready() -> void: if _initialized: return; _initialized=true
func validate(mod_id: String) -> void: config_validated.emit(mod_id)
func report_conflict(a: String, b: String) -> void: conflict_detected.emit(a,b)
func _get_configuration_warnings() -> PackedStringArray: return []