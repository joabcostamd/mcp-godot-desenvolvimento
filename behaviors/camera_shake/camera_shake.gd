## CameraShake — Tremor Sinusoidal de Câmera | Godot 4.7.
##
## Aplica tremor sinusoidal periódico à Camera2D. Diferente de
## ScreenShake (aleatório), este usa onda senoidal com frequência
## configurável para vibração controlada (terremoto, motor, passos).
##
## @behavior: camera_shake
## @genres: platformer, topdown_shooter, rpg, generic
## @tutorial: behaviors/camera_shake/README.md

@tool
class_name CameraShake
extends Node

## Intensidade máxima do deslocamento em pixels.
@export var amplitude: float = 5.0:
	set(v):
		amplitude = clampf(v, 0.1, 100.0)

## Frequência da onda em Hz (ciclos/segundo).
@export var frequency: float = 10.0:
	set(v):
		frequency = clampf(v, 0.5, 60.0)

## Duração total do tremor em segundos.
@export var duration: float = 0.5:
	set(v):
		duration = clampf(v, 0.05, 10.0)

## Fator de decaimento (0 = linear até 0, 1 = sem decaimento).
@export var decay: float = 0.8:
	set(v):
		decay = clampf(v, 0.0, 1.0)

## Direção do tremor: (1,0) = horizontal, (0,1) = vertical, (1,1) = diagonal.
@export var direction: Vector2 = Vector2(1.0, 1.0):
	set(v):
		direction = v.normalized() if v.length_squared() > 0.001 else Vector2.ONE

signal shake_started()
signal shake_finished()

var _elapsed: float = 0.0
var _active: bool = false
var _original_offset: Vector2 = Vector2.ZERO
var _camera: Camera2D = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_camera()
	_initialized = true


func _find_camera() -> void:
	var p := get_parent()
	if p is Camera2D:
		_camera = p as Camera2D


## Dispara o tremor sinusoidal.
## amplitude_override < 0 usa o @export amplitude.
func trigger(amplitude_override: float = -1.0) -> void:
	if _active:
		return  # PADRÃO 10: não interrompe shake em andamento

	if not _camera:
		_find_camera()

	if _camera:
		_original_offset = _camera.offset

	_elapsed = 0.0
	_active = true

	if amplitude_override >= 0.0:
		amplitude = amplitude_override

	shake_started.emit()


## Interrompe o tremor imediatamente, restaurando o offset original.
func stop() -> void:
	if not _active:
		return
	_restore_camera()
	_active = false
	shake_finished.emit()


## Retorna true se o tremor está ativo.
func is_shaking() -> bool:
	return _active


func _process(delta: float) -> void:
	if not _active:
		return

	_elapsed += delta
	if _elapsed >= duration:
		_restore_camera()
		_active = false
		shake_finished.emit()
		return

	var progress := _elapsed / duration
	var current_amp := amplitude * (1.0 - progress * decay)
	var angle := _elapsed * frequency * TAU
	var offset := direction * current_amp * sin(angle)

	if _camera:
		_camera.offset = _original_offset + offset


func _restore_camera() -> void:
	if _camera:
		_camera.offset = _original_offset


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not _camera:
		w.append("Nenhuma Camera2D detectada no parent — adicione como filho de Camera2D.")
	return w
