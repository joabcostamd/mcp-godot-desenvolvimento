## EnemyPatrol — Patrulha entre Waypoints | Godot 4.7 Style Guide compliant.
##
## Node filho de CharacterBody2D que move o pai entre waypoints.
## Espera wait_time segundos em cada ponto. Suporta loop e ping_pong.
## Integra com state_machine (sibling) para estados patrol/idle.
##
## @behavior: enemy_patrol
## @genres: platformer, topdown_shooter, roguelike, metroidvania, stealth, generic
## @tutorial: behaviors/enemy_patrol/README.md

@tool
class_name EnemyPatrol
extends Node

## Lista de posições globais para patrulhar.
@export var waypoints: PackedVector2Array:
	set(v):
		waypoints = v

## Velocidade de movimento (px/s).
@export var speed: float = 100.0:
	set(v):
		speed = clampf(v, 10.0, 2000.0)

## Tempo de espera em cada waypoint (s).
@export var wait_time: float = 1.0:
	set(v):
		wait_time = clampf(v, 0.0, 60.0)
		if _wait_timer:
			_wait_timer.wait_time = wait_time

## Se true, volta ao primeiro waypoint após o último.
@export var loop: bool = true

## Se true, inverte direção nas pontas. Tem precedência sobre loop.
@export var ping_pong: bool = false

## Emitido ao chegar em um waypoint.
signal waypoint_reached(index: int)

## Emitido ao completar a rota (sem loop/ping_pong).
signal patrol_complete()

var _current_index: int = 0
var _direction: int = 1        # +1 avança, -1 retrocede (ping_pong)
var _state: String = "patrol"   # patrol | idle
var _wait_timer: Timer
var _state_machine: StateMachine
var _arrival_threshold: float = 4.0
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_find_state_machine()
	_create_wait_timer()
	if not waypoints.is_empty() and _state_machine:
		_state_machine.set_state("patrol")
	_initialized = true


## Localiza o StateMachine sibling (mesmo pai).
func _find_state_machine() -> void:
	var parent := get_parent()
	if parent:
		for child in parent.get_children():
			if child is StateMachine and child != self:
				_state_machine = child
				return


## Cria o timer de espera. Guard anti-duplicação.
func _create_wait_timer() -> void:
	if _wait_timer:
		return
	_wait_timer = Timer.new()
	_wait_timer.wait_time = wait_time
	_wait_timer.one_shot = true
	_wait_timer.timeout.connect(_on_wait_timeout)
	add_child(_wait_timer)


func _physics_process(_delta: float) -> void:
	if waypoints.is_empty():
		return

	var parent := get_parent()
	if not parent is CharacterBody2D:
		return

	# Sincroniza com state_machine se existir
	if _state_machine:
		var sm_state := _state_machine.get_state()
		if sm_state == "idle" and _state == "patrol":
			_state = "idle"
		elif sm_state == "patrol" and _state == "idle":
			_state = "patrol"

	if _state == "idle":
		parent.velocity = Vector2.ZERO
		return

	# state == patrol: move em direção ao waypoint atual
	var target := waypoints[_current_index]
	var to_target := target - parent.global_position
	var distance := to_target.length()

	if distance < _arrival_threshold:
		_arrive_at_waypoint()
	else:
		parent.velocity = to_target.normalized() * speed


func _arrive_at_waypoint() -> void:
	var parent := get_parent()
	if parent is CharacterBody2D:
		parent.velocity = Vector2.ZERO
		# Snap ao waypoint para evitar drift
		parent.global_position = waypoints[_current_index]

	waypoint_reached.emit(_current_index)
	_state = "idle"
	if _state_machine:
		_state_machine.set_state("idle")

	# Próximo waypoint
	_advance_index()

	if _wait_timer and wait_time > 0.0:
		_wait_timer.start()
	else:
		_resume_patrol()


func _advance_index() -> void:
	if ping_pong:
		var next_idx := _current_index + _direction
		if next_idx >= waypoints.size() or next_idx < 0:
			_direction *= -1
			_current_index += _direction
		else:
			_current_index = next_idx
	elif loop:
		_current_index = (_current_index + 1) % waypoints.size()
	else:
		_current_index += 1
		if _current_index >= waypoints.size():
			patrol_complete.emit()
			_state = "idle"
			return


func _on_wait_timeout() -> void:
	_resume_patrol()


func _resume_patrol() -> void:
	# Só retoma se ainda há waypoints e não completou rota sem loop
	if _current_index < waypoints.size():
		_state = "patrol"
		if _state_machine:
			_state_machine.set_state("patrol")


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if waypoints.is_empty():
		w.append("waypoints está vazio — EnemyPatrol não fará nada.")
	var parent := get_parent()
	if parent and not parent is CharacterBody2D:
		w.append("O pai deve ser CharacterBody2D para o movimento funcionar.")
	return w
