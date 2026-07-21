## Flee — Fuga Condicional | Godot 4.7 Style Guide compliant.
##
## Node filho de CharacterBody2D que foge de uma ameaça quando a
## condição é atendida (vida baixa, ao tomar dano, ou sempre).
## Integra com state_machine (sibling) para estados flee/safe.
##
## @behavior: flee
## @genres: topdown_shooter, platformer, roguelike, stealth, generic
## @tutorial: behaviors/flee/README.md

@tool
class_name Flee
extends Node

## Velocidade de fuga (px/s).
@export var flee_speed: float = 200.0:
	set(v):
		flee_speed = clampf(v, 10.0, 2000.0)

## Distância segura da ameaça (px).
@export var safe_distance: float = 400.0:
	set(v):
		safe_distance = clampf(v, 50.0, 5000.0)

## Condição que dispara a fuga.
@export var flee_condition: String = "health_below_30%"

## Porcentagem de HP abaixo da qual foge (0.0–1.0).
@export var health_threshold_pct: float = 0.3:
	set(v):
		health_threshold_pct = clampf(v, 0.0, 1.0)

## Emitido quando começa a fugir.
signal fleeing()

## Emitido quando atinge distância segura.
signal safe()

var _threat: Node2D
var _state: String = "safe"  # safe | flee
var _health: Health
var _state_machine: StateMachine


func _ready() -> void:
	_find_health()
	_find_state_machine()
	_find_threat()


func _physics_process(_delta: float) -> void:
	_evaluate_condition()

	var parent := get_parent()

	if _state == "safe":
		if parent is CharacterBody2D:
			parent.velocity = Vector2.ZERO
		return

	# state == flee
	if not parent is CharacterBody2D:
		return

	# P8: threat pode ter sido removida
	if not is_instance_valid(_threat):
		_threat = null
		_set_safe()
		return

	var to_threat := parent.global_position - _threat.global_position
	var distance := to_threat.length()

	if distance >= safe_distance:
		_set_safe()
		return

	# Foge na direção oposta à ameaça
	if distance > 0.01:
		parent.velocity = to_threat.normalized() * flee_speed


## Avalia a condição de fuga e transiciona flee/safe.
func _evaluate_condition() -> void:
	match flee_condition:
		"always":
			if _state == "safe":
				_set_flee()
		"health_below_30%":
			if _health and is_instance_valid(_health):
				var pct := float(_health.current_hp) / float(_health.max_hp)
				if pct <= health_threshold_pct:
					if _state == "safe":
						_set_flee()
				else:
					if _state == "flee":
						_set_safe()
		_:
			# Condição desconhecida — mantém estado atual
			pass


## Conecta ao sinal damage_taken do Health para condição on_damage.
func _on_damage_taken(_amount: int, _remaining: int) -> void:
	if flee_condition == "on_damage" and _state == "safe":
		_set_flee()


func _set_flee() -> void:
	if _state == "flee":
		return
	_state = "flee"
	fleeing.emit()
	if _state_machine:
		_state_machine.set_state("flee")


func _set_safe() -> void:
	if _state == "safe":
		return
	_state = "safe"
	safe.emit()
	if _state_machine:
		_state_machine.set_state("safe")


func _find_health() -> void:
	var parent := get_parent()
	if parent:
		for child in parent.get_children():
			if child is Health:
				_health = child
				_health.damage_taken.connect(_on_damage_taken)
				return


func _find_state_machine() -> void:
	var parent := get_parent()
	if parent:
		for child in parent.get_children():
			if child is StateMachine and child != self:
				_state_machine = child
				return


func _find_threat() -> void:
	_threat = _find_in_group("player")


func _find_in_group(group_name: String) -> Node2D:
	var tree := get_tree()
	if tree:
		var nodes := tree.get_nodes_in_group(group_name)
		if nodes.size() > 0:
			return nodes[0] as Node2D
	return null


## Define a ameaça manualmente (sobrescreve detecção automática).
func set_threat(node: Node2D) -> void:
	_threat = node


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	var parent := get_parent()
	if parent and not parent is CharacterBody2D:
		w.append("O pai deve ser CharacterBody2D para o movimento funcionar.")
	if not _health:
		w.append("Nenhum Health sibling encontrado — flee_condition 'health_below_30%' não funcionará.")
	return w
