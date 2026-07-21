## PauseMenu — Sistema de Pausa | Godot 4.7 Style Guide compliant.
##
## Pausa/retoma a árvore via get_tree().paused.
## Detecta input (ui_cancel) e emite paused/resumed.
##
## @behavior: pause_menu
## @genres: generic
## @tutorial: behaviors/pause_menu/README.md

@tool
class_name PauseMenu
extends Node

## InputMap action para toggle.
@export var pause_action: String = "ui_cancel"

signal paused()
signal resumed()

var _is_paused: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_initialized = true


func _input(event: InputEvent) -> void:
	if Engine.is_editor_hint(): return
	if event.is_action_pressed(pause_action):
		toggle()


## Alterna entre pausado e rodando.
func toggle() -> void:
	if _is_paused:
		resume()
	else:
		pause()


## Pausa o jogo.
func pause() -> void:
	if _is_paused: return
	if not is_inside_tree(): return
	get_tree().paused = true
	_is_paused = true
	paused.emit()


## Retoma o jogo.
func resume() -> void:
	if not _is_paused: return
	if not is_inside_tree(): return
	get_tree().paused = false
	_is_paused = false
	resumed.emit()


func is_paused() -> bool:
	return _is_paused
