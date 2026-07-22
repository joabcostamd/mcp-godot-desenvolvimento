## rpg_main.gd — MCP Example | Script principal do RPG Top-Down.
##
## Conecta behaviors e gerencia fluxo de jogo (explorar → combater → dialogar).

extends Node2D

@onready var player: CharacterBody2D = $Player
@onready var health: Node = $Player/Health
@onready var xp: Node = $Player/XP
@onready var dialogue: Node = $UI/Dialogue


func _ready() -> void:
	if health and health.has_signal("died"):
		health.connect("died", _on_player_died)

	if xp and xp.has_signal("leveled_up"):
		xp.connect("leveled_up", _on_level_up)

	print_rich("[RPG] Pronto! WASD para mover, Espaco para atacar, E para interagir.")


func _on_player_died() -> void:
	if get_tree():
		get_tree().change_scene_to_file("res://scenes/game_over.tscn")


func _on_level_up() -> void:
	print_rich("[RPG] Level up!")
