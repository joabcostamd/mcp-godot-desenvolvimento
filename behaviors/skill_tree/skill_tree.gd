## SkillTree — Arvore de Habilidades | Godot 4.7.
##
## Node que gerencia uma arvore de habilidades com nos conectados.
## Cada no tem custo, prerequisitos (nos conectados que devem
## estar desbloqueados), e bonus de atributos. Integra com
## CharacterStats sibling para aplicar bonus.
##
## @behavior: skill_tree
## @genres: rpg, roguelike, generic
## @tutorial: behaviors/skill_tree/README.md

@tool
class_name SkillTree
extends Node

## Pontos disponiveis para desbloquear nos.
@export var available_points: int = 0:
	set(v):
		available_points = maxi(0, v)
		points_changed.emit(available_points)

signal node_unlocked(node_id: String)
signal tree_reset()
signal points_changed(available: int)

## Estrutura: { node_id: { "name": str, "cost": int, "connections": [str],
##   "bonuses": { "strength": int, ... }, "unlocked": bool } }
var _nodes: Dictionary = {}
var _unlocked: Array[String] = []
var _stats: CharacterStats = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_stats()
	_initialized = true


func _find_stats() -> void:
	var parent := get_parent()
	if not parent:
		return
	for child in parent.get_children():
		if child is CharacterStats:
			_stats = child as CharacterStats
			return


## Adiciona um no a arvore.
## @param node_id: identificador unico
## @param name_pt: nome exibido
## @param cost: custo em pontos
## @param connections: IDs dos nos conectados (prerequisitos)
## @param bonuses: dicionario de bonus (ex: {"strength": 5})
func add_node(node_id: String, name_pt: String, cost: int, connections: Array = [], bonuses: Dictionary = {}) -> void:
	_nodes[node_id] = {
		"name": name_pt,
		"cost": maxi(1, cost),
		"connections": connections.duplicate(),
		"bonuses": bonuses.duplicate(),
		"unlocked": false
	}


## Tenta desbloquear um no. Retorna true se sucesso.
## Requer: pontos suficientes, prerequisitos desbloqueados, nao ja desbloqueado.
func unlock_node(node_id: String) -> bool:
	if not _nodes.has(node_id):
		return false

	var node: Dictionary = _nodes[node_id]
	if node.unlocked:
		return false

	var cost: int = node.cost
	if available_points < cost:
		return false

	# Verifica prerequisitos (nos conectados)
	for conn_id in node.connections:
		if conn_id not in _unlocked:
			return false

	# Gasta pontos
	available_points -= cost

	# Desbloqueia
	node.unlocked = true
	_unlocked.append(node_id)

	# Aplica bonus
	_apply_bonuses(node.bonuses)

	node_unlocked.emit(node_id)
	return true


## Reseta toda a arvore (remove todos os desbloqueios e devolve pontos).
func reset_tree() -> void:
	var refund := 0
	for node_id in _unlocked:
		var node: Dictionary = _nodes.get(node_id, {})
		if not node.is_empty():
			_remove_bonuses(node.bonuses)
			refund += node.cost
			node.unlocked = false

	_unlocked.clear()
	available_points += refund
	tree_reset.emit()


## Retorna true se o no esta desbloqueado.
func is_unlocked(node_id: String) -> bool:
	return node_id in _unlocked


## Retorna true se o no pode ser desbloqueado (tem pontos e prerequisitos).
func can_unlock(node_id: String) -> bool:
	if not _nodes.has(node_id):
		return false
	var node: Dictionary = _nodes[node_id]
	if node.unlocked:
		return false
	if available_points < node.cost:
		return false
	for conn_id in node.connections:
		if conn_id not in _unlocked:
			return false
	return true


## Retorna os IDs dos nos desbloqueados.
func get_unlocked_nodes() -> Array[String]:
	return _unlocked.duplicate()


## Adiciona pontos disponiveis (ex: ao subir de nivel).
func add_points(amount: int) -> void:
	available_points += maxi(0, amount)


## Retorna o custo total de pontos ja gastos.
func get_total_spent() -> int:
	var total := 0
	for node_id in _unlocked:
		total += _nodes[node_id].cost
	return total


func _apply_bonuses(bonuses: Dictionary) -> void:
	if not _stats:
		return
	for stat_name in bonuses.keys():
		var value: float = bonuses[stat_name]
		if value != 0:
			_stats.add_modifier(stat_name, 1.0 + value * 0.01)


func _remove_bonuses(bonuses: Dictionary) -> void:
	if not _stats:
		return
	for stat_name in bonuses.keys():
		_stats.clear_modifiers(stat_name)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if _nodes.is_empty():
		w.append("No skill nodes defined — use add_node() to build the tree.")
	if not _stats:
		w.append("No CharacterStats sibling found — stat bonuses will not be applied.")
	return w
