## Currency — Componente de Moeda | Godot 4.7 Style Guide compliant.
##
## Gerencia moeda genérica com tipo nomeado. Operações: add, spend, can_afford.
## Emite gained, spent e insufficient. Múltiplas instâncias com tipos
## diferentes podem coexistir no mesmo nó (ex: gold + gems).
##
## @behavior: currency
## @genres: platformer, topdown_shooter, rpg, roguelike, tower_defense, idle, generic
## @tutorial: behaviors/currency/README.md

@tool
class_name Currency
extends Node

## Nome do tipo de moeda.
@export var currency_type: String = "gold"

## Quantidade atual.
@export var amount: int = 0:
	set(v):
		amount = clampi(v, 0, 999999)

## Emitido ao ganhar moeda.
signal gained(value: int, new_total: int)

## Emitido ao gastar moeda com sucesso.
signal spent(value: int, new_total: int)

## Emitido ao tentar gastar sem saldo suficiente.
signal insufficient(requested: int, available: int)

var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_initialized = true


## Adiciona moeda. value <= 0 é no-op (não emite sinal).
func add(value: int) -> void:
	if value <= 0:
		return
	amount += value
	gained.emit(value, amount)


## Gasta moeda se houver saldo. Retorna true no sucesso.
## value <= 0 retorna true (gasto zero é válido, no-op).
func spend(value: int) -> bool:
	if value < 0:
		return false
	if value == 0:
		return true
	if not can_afford(value):
		insufficient.emit(value, amount)
		return false
	amount -= value
	spent.emit(value, amount)
	return true


## Verifica se há saldo suficiente.
func can_afford(value: int) -> bool:
	if value <= 0:
		return true
	return amount >= value


## Retorna a quantidade atual.
func get_amount() -> int:
	return amount


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if currency_type.is_empty():
		w.append("currency_type está vazio — considere nomear o tipo de moeda.")
	return w
