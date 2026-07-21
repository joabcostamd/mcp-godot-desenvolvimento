## Behavior auto_save para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: auto_save
@tool class_name AutoSave extends Node
@export var interval: float = 60.0: set(v)=interval=clampf(v,5.0,3600.0)
@export var save_on_scene_change: bool = true
signal auto_saved()
var _timer: float = 0.0; var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func _process(delta: float) -> void: _timer+=delta; if _timer>=interval: _timer=0.0; auto_saved.emit()
func trigger_save() -> void: _timer=0.0; auto_saved.emit()
func _get_configuration_warnings() -> PackedStringArray: return []
