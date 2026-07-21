## Destructible — Objeto Destrutível | Godot 4.7.
##
## Node2D que escuta Health sibling. Emite destroyed ao zerar HP.
## Suporta efeito de destruição e drop_table.
##
## @behavior: destructible

@tool
class_name Destructible
extends Node2D

@export var destroy_effect: String = ""
@export var auto_detect_health: bool = true

signal damaged(current_hp: int)
signal destroyed()

var _health: Health = null
var _destroyed: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	if auto_detect_health: _find_health()
	_initialized = true


func _find_health() -> void:
	var parent := get_parent()
	if not parent: return
	for c in parent.get_children():
		if c is Health:
			_health = c as Health
			if not _health.damage_taken.is_connected(_on_damage):
				_health.damage_taken.connect(_on_damage)
			if not _health.died.is_connected(_on_zero_hp):
				_health.died.connect(_on_zero_hp)
			return


func _on_damage(_amount: int, current: int) -> void:
	if _destroyed: return
	damaged.emit(current)


func _on_zero_hp() -> void:
	if _destroyed: return
	_destroyed = true
	_spawn_effect()
	destroyed.emit()


func _spawn_effect() -> void:
	if destroy_effect.is_empty(): return
	var res := load(destroy_effect)
	if not res: return
	var inst := res.instantiate()
	if inst is Node2D:
		var p := get_parent()
		if p and p is Node2D:
			(p as Node2D).get_parent().add_child(inst)
			(inst as Node2D).global_position = (p as Node2D).global_position


func is_destroyed() -> bool:
	return _destroyed
