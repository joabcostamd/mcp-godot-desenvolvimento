## Quest — Sistema de Quests | Godot 4.7 Style Guide compliant.
##
## Gerencia quests com objetivos rastreáveis e recompensas.
## Auto-detecta Inventory e Currency irmãos, conecta sinais.
##
## @behavior: quest
## @genres: rpg, roguelike, platformer, topdown_shooter, generic
## @tutorial: behaviors/quest/README.md

@tool
class_name Quest
extends Node

## Lista de quests: [{id, name, objectives: [{type, target_id, required}], rewards: [{type, target_id, quantity}]}]
@export var quests: Array = []

## Emitido ao iniciar quest.
signal quest_started(quest_id: String)

## Emitido ao concluir quest.
signal quest_completed(quest_id: String)

## Emitido ao falhar quest.
signal quest_failed(quest_id: String)

var _inventory: Inventory = null
var _currency: Currency = null
var _active_quests: Dictionary = {}   # quest_id → {objectives: [{current, required, type, target_id}]}
var _completed_quests: Array[String] = []
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_dependencies()
	_initialized = true


func _find_dependencies() -> void:
	var parent_node := get_parent()
	if not parent_node:
		return
	for child in parent_node.get_children():
		if child is Inventory and not _inventory:
			_inventory = child as Inventory
			if not _inventory.item_added.is_connected(_on_item_added):
				_inventory.item_added.connect(_on_item_added)
		if child is Currency and not _currency:
			_currency = child as Currency
			if not _currency.spent.is_connected(_on_currency_spent):
				_currency.spent.connect(_on_currency_spent)


## Inicia uma quest pelo ID. Retorna true se iniciada com sucesso.
func start_quest(quest_id: String) -> bool:
	if quest_id.is_empty():
		return false
	if _active_quests.has(quest_id):
		return false
	if quest_id in _completed_quests:
		return false

	var quest_def := _find_quest_def(quest_id)
	if quest_def.is_empty():
		return false

	var objectives := []
	for obj in quest_def.get("objectives", []):
		var obj_dict := obj as Dictionary
		objectives.append({
			"type": obj_dict.get("type", ""),
			"target_id": obj_dict.get("target_id", ""),
			"required": obj_dict.get("required", 0) as int,
			"current": 0
		})

	_active_quests[quest_id] = {"objectives": objectives}
	quest_started.emit(quest_id)
	_check_completion(quest_id)
	return true


## Retorna o progresso de uma quest: {objectives: [{type, target_id, current, required}], completed: bool}
func get_progress(quest_id: String) -> Dictionary:
	if not _active_quests.has(quest_id):
		return {"objectives": [], "completed": quest_id in _completed_quests}

	var data := _active_quests[quest_id] as Dictionary
	var objectives := data.get("objectives", []) as Array
	return {
		"objectives": objectives.duplicate(true),
		"completed": false
	}


## Verifica se uma quest está ativa.
func is_active(quest_id: String) -> bool:
	return _active_quests.has(quest_id)


## Verifica se uma quest foi completada.
func is_completed(quest_id: String) -> bool:
	return quest_id in _completed_quests


func _find_quest_def(quest_id: String) -> Dictionary:
	for q in quests:
		var q_dict := q as Dictionary
		if q_dict.get("id", "") == quest_id:
			return q_dict
	return {}


func _on_item_added(item_id: String, quantity: int, _slot: int) -> void:
	for quest_id in _active_quests.keys():
		var data := _active_quests[quest_id] as Dictionary
		for obj in data.get("objectives", []):
			var obj_dict := obj as Dictionary
			if obj_dict.type == "collect" and obj_dict.target_id == item_id:
				obj_dict.current = mini(obj_dict.current + quantity, obj_dict.required)
		_check_completion(quest_id)


func _on_currency_spent(_value: int, _new_total: int) -> void:
	# "spend" objectives rastreiam pelo total gasto — usamos _value diretamente
	# mas como o sinal só diz o que foi gasto, precisamos rastrear o accumulating
	# Simplificação: cada gasto incrementa "spend" com target_id = currency_type
	for quest_id in _active_quests.keys():
		var data := _active_quests[quest_id] as Dictionary
		for obj in data.get("objectives", []):
			var obj_dict := obj as Dictionary
			if obj_dict.type == "spend" and _currency:
				# target_id = currency_type da currency irmã
				if obj_dict.target_id == _currency.currency_type or obj_dict.target_id.is_empty():
					obj_dict.current = mini(obj_dict.current + _value, obj_dict.required)
		_check_completion(quest_id)


func _check_completion(quest_id: String) -> void:
	if not _active_quests.has(quest_id):
		return

	var data := _active_quests[quest_id] as Dictionary
	for obj in data.get("objectives", []):
		var obj_dict := obj as Dictionary
		if obj_dict.current < obj_dict.required:
			return

	# Todos objetivos cumpridos — dar recompensas e completar
	_grant_rewards(quest_id)
	_active_quests.erase(quest_id)
	_completed_quests.append(quest_id)
	quest_completed.emit(quest_id)


func _grant_rewards(quest_id: String) -> void:
	var quest_def := _find_quest_def(quest_id)
	for reward in quest_def.get("rewards", []):
		var r := reward as Dictionary
		var rtype := r.get("type", "") as String
		var target_id := r.get("target_id", "") as String
		var qty := r.get("quantity", 0) as int

		if rtype == "item" and _inventory:
			_inventory.add_item(target_id, qty)
		elif rtype == "currency" and _currency:
			_currency.add(qty)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if quests.is_empty():
		w.append("quests está vazio — nenhuma quest definida.")
	if not _inventory:
		w.append("Nenhum Inventory irmão — objetivos 'collect' não serão rastreados.")
	if not _currency:
		w.append("Nenhum Currency irmão — objetivos 'spend' não serão rastreados.")
	return w


## Falha uma quest ativa pelo ID. Emite quest_failed e remove dos ativos.
func fail_quest(quest_id: String) -> void:
	if not _active_quests.has(quest_id):
		return
	_active_quests.erase(quest_id)
	quest_failed.emit(quest_id)
