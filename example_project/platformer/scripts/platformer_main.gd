## platformer_main.gd — MCP Example | Script principal do Platformer.
##
## Conecta behaviors e gerencia o fluxo do jogo.
## Todos os behaviors sao nos filhos na cena — zero codigo de gameplay aqui.

extends Node2D

# ── Referencias aos nos (setados pela cena) ───────────────────────────────────

@onready var player: CharacterBody2D = $Player
@onready var health: Node = $Player/Health
@onready var camera: Node = $Camera
@onready var score: Node = $HUD/Score
@onready var enemies: Node = $Enemies
@onready var coins: Node = $Coins


# ── Ciclo de vida ─────────────────────────────────────────────────────────────

func _ready() -> void:
	# Conectar sinal de morte do jogador
	if health and health.has_signal("died"):
		health.connect("died", _on_player_died)

	# Conectar vitoria (checkpoint final / bandeira)
	var flag: Area2D = get_node_or_null("Flag") as Area2D
	if flag and flag.has_signal("body_entered"):
		flag.connect("body_entered", _on_flag_reached)

	# Conectar moedas ao score
	for coin: Area2D in coins.get_children():
		if coin.has_signal("collected"):
			coin.connect("collected", _on_coin_collected)

	print_rich("[Platformer] Pronto! Use <- -> para andar, Espaco para pular.")


func _on_player_died() -> void:
	print_rich("[Platformer] Player morreu!")
	if get_tree():
		get_tree().change_scene_to_file("res://scenes/game_over.tscn")


func _on_flag_reached(body: Node2D) -> void:
	if body == player:
		print_rich("[Platformer] Bandeira alcancada — VITORIA!")
		if get_tree():
			get_tree().change_scene_to_file("res://scenes/victory.tscn")


func _on_coin_collected() -> void:
	if score and score.has_method("add_points"):
		score.call("add_points", 10)
