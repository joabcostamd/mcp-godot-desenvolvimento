## Enemy Chase Basic — Godot 4.7 Style Guide compliant.
##
## CharacterBody2D que persegue o player (grupo "player").
## Adicione o player ao grupo "player" para o inimigo detecta-lo.
##
## @behavior: enemy_chase
## @genres: topdown_shooter, platformer, roguelike, bullet_hell
## @tutorial: templates/enemy_chase_basic.gd

class_name EnemyChaser
{% raw %}extends CharacterBody2D

@export var speed: float = 150.0
{% endraw %}
var _player: Node2D


func _ready() -> void:
	_player = get_tree().get_first_node_in_group("player")


func _physics_process(_delta: float) -> void:
	if not _player:
		return
	var direction := (_player.global_position - global_position).normalized()
	velocity = direction * speed
	move_and_slide()
