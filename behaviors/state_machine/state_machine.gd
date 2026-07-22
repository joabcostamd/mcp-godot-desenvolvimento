## StateMachine — FSM Leve | Godot 4.7 Style Guide compliant.
##
## Máquina de estados finita baseada em condições.
## Configure estados e transições, depois chame trigger(condition).
## Outros behaviors consultam get_state() para decidir comportamento.
##
## @behavior: state_machine
## @genres: platformer, topdown_shooter, rpg, roguelike, fighting,
##          metroidvania, bullet_hell, generic
## @tutorial: behaviors/state_machine/README.md

@tool
class_name StateMachine
extends Node

## Estado inicial.
@export var default_state: String = "idle"

## Emitido em toda transição.
signal state_changed(from_state: String, to_state: String)

## Emitido ao entrar no novo estado.
signal state_entered(state: String)

## Emitido ao sair do estado antigo.
signal state_exited(state: String)

var _states: Dictionary = {}           # nome → {} (metadados futuros)
var _transitions: Array[Dictionary] = []  # {from, to, condition}
var _current_state: String = ""
var _initialized: bool = false


func _ready() -> void:
	if not _initialized:
		_initialize()


func _initialize() -> void:
	if _states.is_empty():
		_states[default_state] = {}
	_current_state = default_state
	_initialized = true


## Configura estados, transições e estado inicial de uma vez.
## states: Array[String] — nomes dos estados
## transitions: Array[Dictionary] — [{from, to, condition}, ...]
## default: String — estado inicial (opcional, usa default_state se omitido)
func configure(states: Array, transitions: Array[Dictionary], default := "") -> void:
	_states.clear()
	for s in states:
		_states[s] = {}

	_transitions = transitions.duplicate()

	if not default.is_empty():
		default_state = default

	# Se o default_state não está entre os estados configurados, usa o primeiro
	if not _states.has(default_state):
		if states.size() > 0:
			default_state = states[0]

	_initialized = true
	if is_inside_tree():
		_current_state = default_state


## Dispara uma condição. Se houver transição aplicável, muda de estado.
## Retorna true se houve transição.
func trigger(condition: String) -> bool:
	if not _initialized:
		return false

	for trans in _transitions:
		var from_match: bool = trans["from"] == _current_state or trans["from"] == "any"
		var cond_match: bool = trans["condition"] == condition
		if from_match and cond_match:
			var to_state: String = trans["to"]
			if not _states.has(to_state):
				return false
			_set_state_internal(to_state)
			return true

	return false


## Força mudança para um estado (ignora condições de transição).
## Retorna false se o estado não existe.
func set_state(state: String) -> bool:
	if not _states.has(state):
		return false
	_set_state_internal(state)
	return true


## Retorna o estado atual.
func get_state() -> String:
	return _current_state


## Verifica se está em um estado específico.
func is_state(state: String) -> bool:
	return _current_state == state


## Retorna a lista de estados configurados.
func get_states() -> Array:
	return _states.keys()


func _set_state_internal(new_state: String) -> void:
	var old := _current_state
	if new_state == old:
		return
	_current_state = new_state

	state_exited.emit(old)
	state_entered.emit(new_state)
	state_changed.emit(old, new_state)


## Auto-documentação no editor.
func _get_configuration_warnings() -> PackedStringArray:
	var warnings: PackedStringArray = []
	if _states.is_empty():
		warnings.append("Nenhum estado configurado. Use configure() ou defina default_state.")
	if _transitions.is_empty():
		warnings.append("Nenhuma transição configurada. Use configure() para adicionar transições.")
	# Valida que todas as transições apontam para estados existentes
	for trans in _transitions:
		if not _states.has(trans["to"]):
			warnings.append("Transição '" + trans["from"] + " → " + trans["to"] + "': estado destino '" + trans["to"] + "' não configurado.")
			break
	return warnings
