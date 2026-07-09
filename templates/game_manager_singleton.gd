## Game Manager Singleton — Godot 4.7 Style Guide compliant.
##
## Autoload global para score, vidas e high score.
## Configure como autoload: nome "GameManager".

class_name GameManager
{% raw %}extends Node

signal score_changed(new_score: int)
signal lives_changed(new_lives: int)
signal game_over(final_score: int)

var score: int = 0
var lives: int = 3
{% endraw %}
var high_score: int = 0


func add_score(points: int) -> void:
	score += points
	score_changed.emit(score)
	if score > high_score:
		high_score = score


func lose_life() -> void:
	lives -= 1
	lives_changed.emit(lives)
	if lives <= 0:
		game_over.emit(score)
		get_tree().paused = true


func reset_game() -> void:
	score = 0
	lives = 3
	get_tree().paused = false
