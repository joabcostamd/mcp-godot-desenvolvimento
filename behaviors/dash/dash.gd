## Dash — Impulso Rápido | Godot 4.7.
##
## Node filho de CharacterBody2D. Ao pressionar a ação de dash,
## aplica velocidade na direção do input por dash_duration segundos.
## Cooldown controlado por Timer.
##
## @behavior: dash
## @genres: platformer, topdown_shooter, metroidvania, roguelike, generic
## @tutorial: behaviors/dash/README.md

@tool
class_name Dash
extends Node

## Velocidade durante o dash (px/s).
@export var dash_speed: float = 800.0:
	set(v):
		dash_speed = clampf(v, 100.0, 5000.0)

## Duração do dash (s).
@export var dash_duration: float = 0.15:
	set(v):
		dash_duration = clampf(v, 0.05, 1.0)
		if _dash_timer:
			_dash_timer.wait_time = dash_duration

## Cooldown entre dashes (s).
@export var cooldown: float = 0.5:
	set(v):
		cooldown = clampf(v, 0.0, 10.0)
		if _cooldown_timer:
			_cooldown_timer.wait_time = cooldown

## Se false, não processa input de dash.
@export var enabled: bool = true

signal dashed()
signal dash_ready()

var _dash_timer: Timer
var _cooldown_timer: Timer
var _dashing: bool = false
var _can_dash: bool = true
var _dash_direction: Vector2 = Vector2.RIGHT
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_create_timers()
	_initialized = true


func _create_timers() -> void:
	if _dash_timer:
		return

	_dash_timer = Timer.new()
	_dash_timer.name = "DashTimer"
	_dash_timer.one_shot = true
	_dash_timer.wait_time = dash_duration
	_dash_timer.timeout.connect(_end_dash)
	add_child(_dash_timer)

	_cooldown_timer = Timer.new()
	_cooldown_timer.name = "CooldownTimer"
	_cooldown_timer.one_shot = true
	_cooldown_timer.wait_time = cooldown
	_cooldown_timer.timeout.connect(_on_cooldown_ready)
	add_child(_cooldown_timer)


func _physics_process(_delta: float) -> void:
	if not enabled:
		return

	if not _dashing:
		# Tenta iniciar dash
		if _can_dash and Input.is_action_just_pressed("ui_accept"):
			var dir := _get_dash_direction()
			if dir.length_squared() > 0.01:
				_start_dash(dir.normalized())
		return

	# Durante o dash: mantém velocidade fixa
	var parent := get_parent()
	if parent is CharacterBody2D:
		parent.velocity = _dash_direction * dash_speed


func _get_dash_direction() -> Vector2:
	var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if dir.length_squared() > 0.01:
		_dash_direction = dir.normalized()
	elif _dash_direction.length_squared() < 0.01:
		_dash_direction = Vector2.RIGHT
	return _dash_direction


func _start_dash(dir: Vector2) -> void:
	_dashing = true
	_can_dash = false
	_dash_direction = dir

	if _dash_timer:
		_dash_timer.start()
	if _cooldown_timer:
		_cooldown_timer.start()

	dashed.emit()


func _end_dash() -> void:
	_dashing = false


func _on_cooldown_ready() -> void:
	_can_dash = true
	dash_ready.emit()


## Retorna true se está no meio de um dash.
func is_dashing() -> bool:
	return _dashing


## Retorna true se o dash está disponível.
func can_dash() -> bool:
	return _can_dash and not _dashing


## Cancela o dash atual (útil ao tomar dano).
func cancel_dash() -> void:
	if _dashing and _dash_timer:
		_dash_timer.stop()
	_dashing = false


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if cooldown <= 0.0:
		w.append("cooldown is 0 — dash can be spammed with no limit.")
	return w
