## IdleGenerator — Gerador de Recursos Idle/Clicker | Godot 4.7.
##
## Node que gera recursos automaticamente ao longo do tempo.
## Acumula até max_storage. Transfere para Currency sibling via
## collect(). Suporta upgrade com custo escalável que aumenta
## a taxa de produção.
##
## @behavior: idle_generator
## @genres: idle, clicker, generic
## @tutorial: behaviors/idle_generator/README.md

@tool
class_name IdleGenerator
extends Node

## Taxa base de produção (unidades/segundo) no nível 1.
@export var resource_per_second: float = 1.0:
	set(v):
		resource_per_second = clampf(v, 0.1, 1000.0)

## Capacidade máxima de armazenamento.
@export var max_storage: float = 100.0:
	set(v):
		max_storage = clampf(v, 1.0, 1000000.0)

## Custo base (em moeda) para o primeiro upgrade.
@export var upgrade_cost: int = 10:
	set(v):
		upgrade_cost = clampi(v, 1, 999999)

## Multiplicador do custo a cada upgrade.
@export var upgrade_cost_multiplier: float = 1.5:
	set(v):
		upgrade_cost_multiplier = clampf(v, 1.0, 10.0)

## Multiplicador da taxa de produção a cada upgrade.
@export var upgrade_rate_multiplier: float = 2.0:
	set(v):
		upgrade_rate_multiplier = clampf(v, 1.0, 5.0)

## Se false, pausa a geração de recursos.
@export var enabled: bool = true

signal generated(amount: int)
signal storage_full()
signal upgraded(new_level: int, new_rate: float)

var _level: int = 1
var _stored: float = 0.0
var _currency: Currency = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_currency()
	_initialized = true


func _find_currency() -> void:
	var parent := get_parent()
	if not parent:
		return
	for child in parent.get_children():
		if child is Currency and not _currency:
			_currency = child as Currency
			return


func _physics_process(delta: float) -> void:
	if not enabled:
		return
	if not _initialized:
		return

	_stored = minf(_stored + delta * get_current_rate(), max_storage)

	if _stored >= max_storage:
		storage_full.emit()


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

## Coleta os recursos acumulados e transfere para Currency sibling.
## Retorna a quantidade coletada (0 se nada acumulado ou sem Currency).
func collect() -> int:
	if _stored < 1.0:
		return 0

	var amount := int(floor(_stored))
	_stored -= float(amount)

	if _currency:
		_currency.add(amount)

	generated.emit(amount)
	return amount


## Realiza um upgrade se houver moeda suficiente.
## Custo = upgrade_cost * (upgrade_cost_multiplier ^ (level - 1))
## Retorna true se o upgrade foi aplicado.
func upgrade() -> bool:
	if not _currency:
		push_warning("IdleGenerator: nenhum Currency sibling — upgrade requer moeda.")
		return false

	var cost := get_upgrade_cost()
	if not _currency.spend(cost):
		return false

	_level += 1
	var new_rate := get_current_rate()
	upgraded.emit(_level, new_rate)
	return true


## Retorna o nível atual do gerador (começa em 1).
func get_level() -> int:
	return _level


## Retorna a taxa de produção atual (resource_per_second * rate_multiplier^(level-1)).
func get_current_rate() -> float:
	return resource_per_second * pow(upgrade_rate_multiplier, float(_level - 1))


## Retorna a quantidade armazenada atualmente (não coletada).
func get_stored() -> float:
	return _stored


## Retorna o custo do próximo upgrade.
func get_upgrade_cost() -> int:
	return int(round(float(upgrade_cost) * pow(upgrade_cost_multiplier, float(_level - 1))))


## Retorna a porcentagem de armazenamento preenchido (0.0 a 1.0).
func get_storage_ratio() -> float:
	if max_storage <= 0.0:
		return 0.0
	return clampf(_stored / max_storage, 0.0, 1.0)


# ---------------------------------------------------------------------------
# INTERNAL
# ---------------------------------------------------------------------------

func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not _currency:
		w.append("Nenhum Currency sibling detectado — collect() não transferirá recursos.")
	if not enabled:
		w.append("enabled está false — o gerador não produzirá recursos.")
	return w
