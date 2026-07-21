## Teleport — Teletransporte | Godot 4.7.
##
## Area2D que teleporta o player ao entrar. Suporta destino local
## (target_position) ou mudança de cena (target_scene com SceneTransition).
##
## @behavior: teleport
## @genres: generic

@tool
class_name Teleport
extends Area2D

@export var target_position: Vector2 = Vector2.ZERO
@export var target_scene: String = ""
@export var player_group: String = "players"

signal teleported()

var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_setup_collision()
	body_entered.connect(_on_body_entered)
	_initialized = true


func _setup_collision() -> void:
	var shape := CollisionShape2D.new(); shape.name = "TeleportShape"
	var rect := RectangleShape2D.new(); rect.size = Vector2(64, 64)
	shape.shape = rect; add_child(shape)


func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group(player_group): return

	if target_scene and ResourceLoader.exists(target_scene):
		var st := SceneTransition.new()
		st.fade_color = Color.BLACK; st.default_duration = 0.5
		add_child(st); st.transition_to(target_scene)
	else:
		body.global_position = target_position

	teleported.emit()
