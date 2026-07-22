## shooter_main.gd — MCP Example | Script principal do Survivors-like.
##
## WASD para mover, tiro automatico, matar inimigos, coletar XP, upgrades.

extends Node2D

@onready var player: CharacterBody2D = $Player
@onready var health: Node = $Player/Health
@onready var spawner: Node = $Spawner
@onready var xp: Node = $Player/XP
@onready var timer_label: Label = $HUD/TimerLabel

var _survival_time: float = 0.0
var _game_over: bool = false


func _ready() -> void:
	if health and health.has_signal("died"):
		health.connect("died", _on_player_died)

	if xp and xp.has_signal("leveled_up"):
		xp.connect("leveled_up", _on_level_up)

	if spawner and spawner.has_method("start_waves"):
		spawner.call("start_waves")

	print_rich("[Shooter] Pronto! WASD para mover. Sobreviva o maximo possivel!")


func _process(delta: float) -> void:
	if _game_over:
		return
	_survival_time += delta
	if timer_label:
		timer_label.text = "Tempo: %.1fs" % _survival_time


func _on_player_died() -> void:
	_game_over = true
	print_rich("[Shooter] Derrota! Sobreviveu %.1f segundos." % _survival_time)
	if get_tree():
		get_tree().change_scene_to_file("res://scenes/game_over.tscn")


func _on_level_up() -> void:
	print_rich("[Shooter] Level up! Escolha um upgrade.")
	if get_tree():
		get_tree().paused = true
		get_tree().change_scene_to_file("res://scenes/upgrade.tscn")
