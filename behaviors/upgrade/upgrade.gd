## Upgrade — Sistema de Upgrade | Godot 4.7 Style Guide compliant.
##
## Escuta leveled_up do XPLevel irmão, oferece escolhas aleatórias
## de upgrades e aplica o escolhido. Estilo Survivors-like.
##
## @behavior: upgrade
## @genres: roguelike, rpg, idle, generic
## @tutorial: behaviors/upgrade/README.md

@tool
class_name Upgrade
extends Node

## Lista de upgrades: [{id, name, max_level, effects: [{stat, value}]}]
@export var upgrade_options: Array = []

## Quantas opções mostrar por level up.
@export var choices_per_level: int = 3:
	set(v):
		choices_per_level = clampi(v, 1, 10)

## Emitido quando há opções disponíveis.
signal choices_ready(options: Array)

## Emitido quando um upgrade é aplicado.
signal upgrade_applied(upgrade_id: String, new_level: int)

var _xp_level: XPLevel = null
var _upgrade_levels: Dictionary = {}  # upgrade_id → current_level
var _pending_choices: Array = []
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_xp_level()
	_initialized = true


func _find_xp_level() -> void:
	var parent_node := get_parent()
	if not parent_node:
		return
	for child in parent_node.get_children():
		if child is XPLevel:
			_xp_level = child as XPLevel
			if not _xp_level.leveled_up.is_connected(_on_leveled_up):
				_xp_level.leveled_up.connect(_on_leveled_up)
			return


func _on_leveled_up(_new_level: int) -> void:
	if upgrade_options.is_empty():
		return
	_pending_choices = _generate_choices()
	if not _pending_choices.is_empty():
		choices_ready.emit(_pending_choices.duplicate())


## Gera opções aleatórias de upgrades ainda não maximizados.
func _generate_choices() -> Array:
	var available := []
	for opt in upgrade_options:
		var opt_dict := opt as Dictionary
		var opt_id := opt_dict.get("id", "") as String
		var max_lvl := opt_dict.get("max_level", 1) as int
		var current_lvl := _upgrade_levels.get(opt_id, 0) as int
		if current_lvl < max_lvl:
			available.append(opt_dict.duplicate())

	if available.is_empty():
		return []

	available.shuffle()
	return available.slice(0, mini(choices_per_level, available.size()))


## Aplica um upgrade pelo índice na lista de opções pendentes.
## Retorna true se aplicado com sucesso.
func apply_upgrade(choice_index: int) -> bool:
	if choice_index < 0 or choice_index >= _pending_choices.size():
		return false

	var chosen := _pending_choices[choice_index] as Dictionary
	var upgrade_id := chosen.get("id", "") as String
	if upgrade_id.is_empty():
		return false

	var current_lvl := _upgrade_levels.get(upgrade_id, 0) as int
	var max_lvl := chosen.get("max_level", 1) as int
	if current_lvl >= max_lvl:
		return false

	_upgrade_levels[upgrade_id] = current_lvl + 1
	_pending_choices.clear()
	upgrade_applied.emit(upgrade_id, current_lvl + 1)
	return true


## Retorna o nível atual de um upgrade específico.
func get_upgrade_level(upgrade_id: String) -> int:
	return _upgrade_levels.get(upgrade_id, 0)


## Retorna as opções pendentes atuais.
func get_pending_choices() -> Array:
	return _pending_choices.duplicate()


## Força a geração de novas opções (útil para testes).
func force_choices() -> void:
	if upgrade_options.is_empty():
		return
	_pending_choices = _generate_choices()
	if not _pending_choices.is_empty():
		choices_ready.emit(_pending_choices.duplicate())


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if upgrade_options.is_empty():
		w.append("upgrade_options está vazio — nenhum upgrade disponível.")
	if not _xp_level:
		var parent_node := get_parent()
		if parent_node:
			var found := false
			for child in parent_node.get_children():
				if child is XPLevel:
					found = true
					break
			if not found:
				w.append("Nenhum XPLevel irmão encontrado — conecte manualmente.")
	return w
