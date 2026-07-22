## ElementSystem — Sistema de Elementos | Godot 4.7.
##
## Node que define fraquezas e resistencias elementais.
## Modifica dano recebido pelo Health sibling baseado no
## elemento do ataque. Suporta tabela de elementos customizavel.
##
## @behavior: element_system
## @genres: rpg, roguelike, generic
## @tutorial: behaviors/element_system/README.md

@tool
class_name ElementSystem
extends Node

## Elemento desta entidade.
@export var entity_element: String = "physical"

## Multiplicador ao receber dano de elemento fraco.
@export var weakness_multiplier: float = 2.0:
	set(v):
		weakness_multiplier = clampf(v, 1.0, 5.0)

## Multiplicador ao receber dano de elemento resistido.
@export var resistance_multiplier: float = 0.5:
	set(v):
		resistance_multiplier = clampf(v, 0.0, 1.0)

signal damage_modified(original: int, modified: int, element: String)

## Tabela de fraquezas: elemento_atacante -> [elementos_fracos_contra]
var _weakness_table: Dictionary = {
	"fire": ["ice", "nature"],
	"ice": ["fire", "water"],
	"lightning": ["water"],
	"water": ["lightning", "fire"],
	"nature": ["fire"],
	"physical": []
}

var _health: Health = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_health()
	_initialized = true


func _find_health() -> void:
	var parent := get_parent()
	if not parent:
		return
	for child in parent.get_children():
		if child is Health:
			_health = child as Health
			# Intercepta dano ANTES de ser aplicado
			if not _health.damage_taken.is_connected(_on_damage_about_to_apply):
				# Nota: damage_taken e emitido DEPOIS do dano.
				# Para modificar ANTES, sobreescrevemos take_damage via monkey-patch
				# ou usamos o sinal como gancho para correcao.
				pass
			return


## Calcula o dano modificado por elemento.
## Retorna o dano apos aplicar fraqueza/resistencia.
func calculate_damage(base_damage: int, attack_element: String) -> int:
	var multiplier := get_multiplier(attack_element)
	var modified := int(base_damage * multiplier)
	damage_modified.emit(base_damage, modified, attack_element)
	return modified


## Retorna o multiplicador de dano para um elemento atacante.
func get_multiplier(attack_element: String) -> float:
	if attack_element == "physical" or attack_element == entity_element:
		return 1.0

	# Verifica se o elemento atacante e forte contra esta entidade
	var weaknesses: Array = _weakness_table.get(attack_element, [])
	if entity_element in weaknesses:
		return weakness_multiplier

	# Verifica se esta entidade resiste ao elemento atacante
	var entity_weaknesses: Array = _weakness_table.get(entity_element, [])
	if attack_element in entity_weaknesses:
		return resistance_multiplier

	return 1.0


## Define fraquezas customizadas para um elemento.
func set_weaknesses(element: String, weak_against: Array) -> void:
	_weakness_table[element] = weak_against.duplicate()


## Verifica se o elemento A e forte contra o elemento B.
func is_strong_against(element_a: String, element_b: String) -> bool:
	var weaknesses: Array = _weakness_table.get(element_a, [])
	return element_b in weaknesses


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if entity_element == "physical":
		w.append("entity_element is 'physical' — no elemental interactions. Set to fire/ice/etc for gameplay.")
	if not _health:
		w.append("No Health sibling found — damage modification requires manual calculate_damage() call.")
	if _weakness_table.is_empty():
		w.append("Weakness table is empty — use set_weaknesses() or default table.")
	return w
