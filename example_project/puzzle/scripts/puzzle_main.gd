## puzzle_main.gd — MCP Example | Script principal do Puzzle Grid.
##
## Movimento em grid, empurrar blocos, verificar vitoria.
## Usa grid_movement behavior + pushable + target_zone.

extends Node2D

@onready var player: CharacterBody2D = $Player
@onready var grid: Node = $Player/GridMovement
@onready var blocks: Node = $Blocks
@onready var targets: Node = $Targets

var _move_count: int = 0


func _ready() -> void:
	if grid and grid.has_signal("moved"):
		grid.connect("moved", _on_move)
	print_rich("[Puzzle] Pronto! Setas para mover, R para reiniciar, Z para desfazer.")


func _on_move() -> void:
	_move_count += 1
	print_rich("[Puzzle] Movimento: %d" % _move_count)
	_check_victory()


func _check_victory() -> void:
	var all_on_target: bool = true
	for block: Area2D in blocks.get_children():
		var on_target: bool = false
		for target: Area2D in targets.get_children():
			if block.global_position.distance_to(target.global_position) < 8.0:
				on_target = true
				break
		if not on_target:
			all_on_target = false
			break
	if all_on_target:
		print_rich("[Puzzle] VITORIA! Todos os blocos nos alvos.")
		if get_tree():
			get_tree().change_scene_to_file("res://scenes/victory.tscn")
