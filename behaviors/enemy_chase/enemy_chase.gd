## EnemyChase — Perseguição ao Jogador | Godot 4.7 Style Guide compliant.
##
## Node filho de CharacterBody2D que persegue o jogador (grupo "player").
## Aplica velocidade ao pai via _physics_process quando dentro do chase_range.
## Desiste quando o jogador sai do lose_range.
##
## @behavior: enemy_chase
## @genres: topdown_shooter, platformer, roguelike, bullet_hell,
##          metroidvania, generic
## @tutorial: behaviors/enemy_chase/README.md

@tool
class_name EnemyChase
extends Node

## Velocidade de perseguição (px/s).
@export var speed: float = 150.0:
	set(value):
		speed = clampf(value, 10.0, 2000.0)

## Distância para começar a perseguir (px).
@export var chase_range: float = 300.0:
	set(value):
		chase_range = clampf(value, 10.0, 5000.0)

## Distância para desistir (px). Deve ser >= chase_range.
@export var lose_range: float = 500.0:
	set(value):
		lose_range = clampf(value, 10.0, 5000.0)

## Emitido ao entrar em perseguição.
signal target_acquired()

## Emitido ao perder o alvo.
signal target_lost()

var _player: Node2D
var _chasing: bool = false
var _stopped: bool = false  # Impede re-aquisição após stop()
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_find_player()
	_initialized = true


func _physics_process(_delta: float) -> void:
	if _stopped:
		return

	# P8: player pode ter sido removido da cena
	if _player and not is_instance_valid(_player):
		_player = null
		_chasing = false

	if not _player:
		_find_player()
		if not _player:
			return

	var parent := get_parent()
	# P1: null guard — parent pode não ser CharacterBody2D
	if not parent is CharacterBody2D:
		return

	var distance := _player.global_position.distance_to(parent.global_position)

	if not _chasing and distance <= chase_range:
		_chasing = true
		target_acquired.emit()

	elif _chasing and distance > lose_range:
		_chasing = false
		parent.velocity = Vector2.ZERO
		target_lost.emit()
		return

	if _chasing:
		var direction := (_player.global_position - parent.global_position).normalized()
		parent.velocity = direction * speed


## Define um alvo manualmente (ignora grupo "player").
func set_target(target: Node2D) -> void:
	_player = target


## Força a busca pelo player no grupo.
func _find_player() -> void:
	if not is_inside_tree():
		return
	var tree := get_tree()
	if tree:
		_player = tree.get_first_node_in_group("player") as Node2D


## Verifica se está perseguindo.
func is_chasing() -> bool:
	return _chasing


## Para a perseguição e impede re-aquisição automática. Use resume() para voltar.
func stop() -> void:
	_stopped = true
	if _chasing:
		_chasing = false
		var parent := get_parent()
		if parent is CharacterBody2D:
			parent.velocity = Vector2.ZERO
		target_lost.emit()


## Retoma a perseguição após stop().
func resume() -> void:
	_stopped = false
	_find_player()


## Auto-documentação no editor.
func _get_configuration_warnings() -> PackedStringArray:
	var warnings: PackedStringArray = []
	var parent := get_parent()
	if parent and not parent is CharacterBody2D:
		warnings.append("Parent não é CharacterBody2D — perseguição não terá efeito.")
	if lose_range < chase_range:
		warnings.append("lose_range < chase_range — inimigo oscilará entre perseguir e parar.")
	if speed <= 10.0:
		warnings.append("speed no mínimo (10 px/s) — movimento quase imperceptível.")
	return warnings
