## FireRate — Controlador de Cadência | Godot 4.7 Style Guide compliant.
##
## Node puro que gerencia cooldown entre disparos com suporte a rajada.
## Use try_fire() para tentar atirar — o componente decide se está pronto.
## Conecte o sinal fired ao spawner de projéteis.
##
## @behavior: fire_rate
## @genres: topdown_shooter, platformer, bullet_hell, roguelike,
##          tower_defense, generic
## @tutorial: behaviors/fire_rate/README.md

@tool
class_name FireRate
extends Node

## Intervalo entre disparos/rajadas (segundos).
@export var fire_interval: float = 0.5:
	set(value):
		fire_interval = clampf(value, 0.05, 60.0)
		if _cooldown_timer:
			_cooldown_timer.wait_time = fire_interval

## Tiros por rajada. 1 = tiro único (semi-auto).
@export var burst_count: int = 1:
	set(value):
		burst_count = clampi(value, 1, 20)

## Intervalo entre tiros dentro da rajada (segundos).
@export var burst_delay: float = 0.1:
	set(value):
		burst_delay = clampf(value, 0.01, 5.0)
		if _burst_timer:
			_burst_timer.wait_time = burst_delay

## Emitido a cada tiro individual.
signal fired()

## Emitido quando o cooldown termina e pode atirar novamente.
signal cooldown_ready()

var _can_fire: bool = true
var _burst_shots_fired: int = 0
var _cooldown_timer: Timer
var _burst_timer: Timer
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_create_timers()
	_initialized = true


func _create_timers() -> void:
	# Evita duplicação se _ready() for chamado múltiplas vezes
	if _cooldown_timer:
		return

	# Timer de cooldown principal (entre rajadas)
	_cooldown_timer = Timer.new()
	_cooldown_timer.name = "CooldownTimer"
	_cooldown_timer.wait_time = fire_interval
	_cooldown_timer.one_shot = true
	_cooldown_timer.timeout.connect(_on_cooldown_finished)
	add_child(_cooldown_timer)

	# Timer de burst (entre tiros da rajada)
	_burst_timer = Timer.new()
	_burst_timer.name = "BurstTimer"
	_burst_timer.wait_time = burst_delay
	_burst_timer.one_shot = true
	_burst_timer.timeout.connect(_on_burst_tick)
	add_child(_burst_timer)


## Tenta disparar. Retorna true se o tiro foi aceito.
func try_fire() -> bool:
	if not _can_fire:
		return false

	_can_fire = false
	_burst_shots_fired = 0
	_do_shot()
	return true


## Verifica se pode atirar (não está em cooldown).
func is_ready() -> bool:
	return _can_fire


## Reseta o cooldown, permitindo atirar imediatamente.
func reset() -> void:
	if _cooldown_timer:
		_cooldown_timer.stop()
	if _burst_timer:
		_burst_timer.stop()
	_can_fire = true
	_burst_shots_fired = 0


func _do_shot() -> void:
	fired.emit()
	_burst_shots_fired += 1

	if _burst_shots_fired < burst_count:
		if _burst_timer:
			_burst_timer.start()
	else:
		if _cooldown_timer:
			_cooldown_timer.start()


func _on_burst_tick() -> void:
	_do_shot()


func _on_cooldown_finished() -> void:
	_can_fire = true
	cooldown_ready.emit()


## Auto-documentação no editor.
func _get_configuration_warnings() -> PackedStringArray:
	var warnings: PackedStringArray = []
	if fire_interval <= 0.05:
		warnings.append("fire_interval muito baixo (≤ 0.05s) — pode causar performance ruim.")
	if burst_count > 1 and burst_delay >= fire_interval:
		warnings.append("burst_delay ≥ fire_interval — a rajada nunca termina antes do próximo cooldown.")
	return warnings
