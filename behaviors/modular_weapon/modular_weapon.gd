## Behavior modular_weapon para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: modular_weapon
@tool class_name ModularWeapon extends Node
signal weapon_assembled(parts: Dictionary); signal stat_recalculated(stats: Dictionary)
var _parts: Dictionary = {}; var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func attach_part(slot: String, part_id: String) -> void: _parts[slot]=part_id; weapon_assembled.emit(_parts)
func remove_part(slot: String) -> void: if _parts.has(slot): _parts.erase(slot); weapon_assembled.emit(_parts)
func get_parts() -> Dictionary: return _parts.duplicate()
func calculate_stats() -> Dictionary: var s:={\"damage\":len(_parts)*10}; stat_recalculated.emit(s); return s
func _get_configuration_warnings() -> PackedStringArray: return []
