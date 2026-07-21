## DoubleJump — Pulo Múltiplo | Godot 4.7.
##
## Node filho de CharacterBody2D. Permite jump_count pulos no ar.
## Coyote time: margem após sair do chão. Reseta ao tocar o chão.
## Complementar ao PlayerController (que cuida do 1º pulo).
##
## @behavior: double_jump
## @genres: platformer, metroidvania, generic
## @tutorial: behaviors/double_jump/README.md

@tool
class_name DoubleJump
extends Node

## Número total de pulos (2 = pulo duplo).
@export var jump_count: int = 2:
	set(v):
		jump_count = clampi(v, 1, 10)

## Velocidade vertical do pulo (negativa = para cima).
@export var jump_velocity: float = -400.0:
	set(v):
		jump_velocity = clampf(v, -2000.0, -50.0)

## Tempo extra após sair do chão (s).
@export var coyote_time: float = 0.1:
	set(v):
		coyote_time = clampf(v, 0.0, 0.5)

signal jumped(jumps_used: int)
signal jumps_exhausted()

var _jumps_used: int = 0
var _was_on_floor: bool = false
var _air_time: float = 0.0
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_initialized = true


func _physics_process(delta: float) -> void:
	var parent := get_parent()
	if not parent is CharacterBody2D:
		return

	var body := parent as CharacterBody2D
	var on_floor := body.is_on_floor()

	# Reset ao tocar o chão
	if on_floor and not _was_on_floor:
		_jumps_used = 0
		_air_time = 0.0

	# Tracking de tempo no ar para coyote time
	if not on_floor:
		_air_time += delta

	# Pulo adicional
	if Input.is_action_just_pressed("ui_accept"):
		if _can_air_jump(on_floor):
			body.velocity.y = jump_velocity
			_jumps_used += 1
			_air_time = 0.0
			jumped.emit(_jumps_used)
			if _jumps_used >= jump_count:
				jumps_exhausted.emit()

	_was_on_floor = on_floor


func _can_air_jump(on_floor: bool) -> bool:
	# No chão: o PlayerController cuida do 1º pulo, não interferimos
	if on_floor:
		return false

	# Já usou todos os pulos
	if _jumps_used >= jump_count:
		return false

	# Coyote time: permite pular mesmo logo após sair do chão
	if _air_time <= coyote_time and _jumps_used == 0:
		return true

	# Pulo no ar normal
	return _jumps_used < jump_count


## Reinicia o contador de pulos.
func reset_jumps() -> void:
	_jumps_used = 0
	_air_time = 0.0


## Retorna quantos pulos já foram usados.
func get_jumps_used() -> int:
	return _jumps_used


## Retorna quantos pulos ainda restam.
func get_jumps_remaining() -> int:
	return maxi(0, jump_count - _jumps_used)
