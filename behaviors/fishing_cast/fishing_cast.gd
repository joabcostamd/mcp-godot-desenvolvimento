## Node que implementa mecânica de pesca com potência de arremesso e minigame.
## Generos: fishing.
## Tags: fishing.
## Extends: Node.
## Sinais: cast(), bite(), caught().
## Dependencias: nenhuma.
## @behavior: fishing_cast
@tool class_name FishingCast extends Node
@export var cast_power: float = 1.0: set(v)=cast_power=clampf(v,0.1,10.0)
@export var minigame_difficulty: float = 1.0: set(v)=minigame_difficulty=clampf(v,0.1,3.0)
signal cast(power: float); signal bite(); signal caught(fish_id: String)
var _is_casting: bool = false
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func start_cast() -> void: _is_casting=true; cast.emit(cast_power)
func on_bite() -> void: if _is_casting: bite.emit()
func catch_fish(fish_id: String) -> void: _is_casting=false; caught.emit(fish_id)
func is_casting() -> bool: return _is_casting
func _get_configuration_warnings() -> PackedStringArray: return []
