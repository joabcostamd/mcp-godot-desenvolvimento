## DamageOverTime — Dano Contínuo | Godot 4.7 Style Guide compliant.
##
## Node que aplica dano periódico a um Health alvo.
## Use start(target_health) para iniciar e stop() para interromper.
##
## @behavior: damage_over_time
## @genres: rpg, roguelike, platformer, topdown_shooter, generic
## @tutorial: behaviors/damage_over_time/README.md

@tool
class_name DamageOverTime
extends Node

## Dano por tick.
@export var damage_per_tick: int = 5:
	set(value):
		damage_per_tick = clampi(value, 1, 9999)

## Intervalo entre ticks (s).
@export var tick_interval: float = 1.0:
	set(value):
		tick_interval = clampf(value, 0.1, 10.0)
		if _tick_timer:
			_tick_timer.wait_time = tick_interval

## Duração total (s).
@export var duration: float = 5.0:
	set(value):
		duration = clampf(value, 0.1, 60.0)

## Emitido a cada tick.
signal dot_tick(damage: int)

## Emitido quando o efeito termina.
signal dot_ended()

var _target_health: Health
var _elapsed: float = 0.0
var _active: bool = false
var _tick_timer: Timer
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_create_timer()
	_initialized = true


func _create_timer() -> void:
	if _tick_timer:
		return

	_tick_timer = Timer.new()
	_tick_timer.name = "DOTTimer"
	_tick_timer.wait_time = tick_interval
	_tick_timer.one_shot = false
	_tick_timer.timeout.connect(_on_tick)
	add_child(_tick_timer)


## Inicia o DOT em um alvo Health. Retorna false se health inválido.
func start(target_health: Health) -> bool:
	if not target_health or not is_instance_valid(target_health):
		return false
	if not target_health.is_alive():
		return false

	_target_health = target_health
	_elapsed = 0.0
	_active = true

	if _tick_timer:
		_tick_timer.start()

	return true


## Interrompe o DOT imediatamente.
func stop() -> void:
	if not _active:
		return
	_active = false
	if _tick_timer:
		_tick_timer.stop()
	_target_health = null
	dot_ended.emit()


## Verifica se o DOT está ativo.
func is_active() -> bool:
	return _active


func _on_tick() -> void:
	if not _active:
		return

	# P8: health pode ter sido removido
	if not _target_health or not is_instance_valid(_target_health):
		stop()
		return

	if not _target_health.is_alive():
		stop()
		return

	var dealt := _target_health.take_damage(damage_per_tick)
	if dealt > 0:
		dot_tick.emit(dealt)

	_elapsed += tick_interval
	if _elapsed >= duration:
		stop()


## Auto-documentação.
func _get_configuration_warnings() -> PackedStringArray:
	var warnings: PackedStringArray = []
	if tick_interval > duration:
		warnings.append("tick_interval > duration — DOT terminará antes do primeiro tick.")
	return warnings
