## SpawnerWave — Spawner de Ondas | Godot 4.7.
##
## Cria inimigos em ondas via ObjectPool. Gerencia intervalo entre
## ondas, spawn delay, máximo de ativos. Conecta Health.died para
## devolver inimigos ao pool automaticamente.
##
## @behavior: spawner_wave
## @genres: survivor_like, tower_defense, bullet_hell, topdown_shooter, generic
## @tutorial: behaviors/spawner_wave/README.md

@tool
class_name SpawnerWave
extends Node

@export var spawn_count_per_wave: int = 10:
	set(v): spawn_count_per_wave = clampi(v, 1, 500)
@export var wave_interval: float = 10.0:
	set(v): wave_interval = clampf(v, 1.0, 300.0)
@export var spawn_delay: float = 0.5:
	set(v):
		spawn_delay = clampf(v, 0.05, 5.0)
		if _spawn_timer:
			_spawn_timer.wait_time = spawn_delay
@export var max_active: int = 50:
	set(v): max_active = clampi(v, 1, 1000)
@export var spawn_radius: float = 300.0:
	set(v): spawn_radius = clampf(v, 10.0, 3000.0)

## Número total de ondas. 0 = infinito.
@export var total_waves: int = 0:
	set(v): total_waves = clampi(v, 0, 999)

signal wave_started(wave_number: int)
signal wave_cleared(wave_number: int)
signal all_waves_done()
signal enemy_spawned(enemy: Node)

var _pool: ObjectPool
var _wave_timer: Timer
var _spawn_timer: Timer
var _current_wave: int = 0
var _spawned_this_wave: int = 0
var _active_enemies: int = 0
var _spawning: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_pool()
	_create_timers()
	if _pool:
		_start_next_wave()
	_initialized = true


func _find_pool() -> void:
	var parent := get_parent()
	if parent:
		for child in parent.get_children():
			if child is ObjectPool and child != self:
				_pool = child
				return


func _create_timers() -> void:
	_wave_timer = Timer.new()
	_wave_timer.one_shot = true
	_wave_timer.timeout.connect(_on_wave_timer_timeout)
	add_child(_wave_timer)

	_spawn_timer = Timer.new()
	_spawn_timer.wait_time = spawn_delay
	_spawn_timer.timeout.connect(_on_spawn_timer_timeout)
	add_child(_spawn_timer)


func _start_next_wave() -> void:
	_current_wave += 1
	_spawned_this_wave = 0
	_spawning = true
	wave_started.emit(_current_wave)
	_try_spawn()


func _on_wave_timer_timeout() -> void:
	_start_next_wave()


func _on_spawn_timer_timeout() -> void:
	_try_spawn()


func _try_spawn() -> void:
	if not _spawning:
		return
	if _active_enemies >= max_active:
		_spawn_timer.start()
		return
	if _spawned_this_wave >= spawn_count_per_wave:
		_spawning = false
		_spawn_timer.stop()
		if _active_enemies == 0:
			_finish_wave()
		return

	if not _pool:
		return
	var enemy := _pool.take()
	if not enemy:
		return

	# Posição aleatória na área de spawn
	var angle := randf_range(0.0, TAU)
	var dist := randf_range(0.0, spawn_radius)
	enemy.global_position = global_position + Vector2.RIGHT.rotated(angle) * dist

	_spawned_this_wave += 1
	_active_enemies += 1
	enemy_spawned.emit(enemy)

	# Auto-retorno ao pool quando morrer
	var health := _find_health(enemy)
	if health:
		health.died.connect(_on_enemy_died.bind(enemy))

	_spawn_timer.start()


func _on_enemy_died(enemy: Node) -> void:
	_active_enemies -= 1
	if _pool:
		_pool.return_object(enemy)

	if not _spawning and _active_enemies == 0:
		_finish_wave()


func _finish_wave() -> void:
	wave_cleared.emit(_current_wave)
	if total_waves > 0 and _current_wave >= total_waves:
		all_waves_done.emit()
		return
	_wave_timer.wait_time = wave_interval
	_wave_timer.start()


func _find_health(node: Node) -> Health:
	for child in node.get_children():
		if child is Health:
			return child
	return null


func get_current_wave() -> int:
	return _current_wave


func get_active_count() -> int:
	return _active_enemies


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not _pool:
		w.append("Nenhum ObjectPool sibling encontrado — spawner não criará inimigos.")
	return w
