## Interactable — Objeto Interagível | Godot 4.7.
##
## Area2D que detecta player e permite interação com ui_accept.
## Suporta hold e sinais focused/unfocused.

@tool
class_name Interactable
extends Area2D

@export var prompt_text: String = ""
@export var player_group: String = "players"
@export var hold_duration: float = 0.0:
	set(v): hold_duration = clampf(v, 0, 5)

signal focused(body: Node2D)
signal unfocused(body: Node2D)
signal interacted(body: Node2D)

var _focused_body: Node2D = null
var _hold_timer: float = 0.0
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_setup_shape()
	body_entered.connect(_on_enter)
	body_exited.connect(_on_exit)
	_initialized = true


func _setup_shape() -> void:
	for c in get_children():
		if c is CollisionShape2D: return
	var s := CollisionShape2D.new(); s.name = "InteractShape"
	var r := RectangleShape2D.new(); r.size = Vector2(48,48)
	s.shape = r; add_child(s)


func _physics_process(delta: float) -> void:
	if not _focused_body: return
	if not is_instance_valid(_focused_body):
		_focused_body = null; return

	if Input.is_action_pressed("ui_accept"):
		_hold_timer += delta
		if hold_duration <= 0.0 or _hold_timer >= hold_duration:
			interacted.emit(_focused_body)
			_hold_timer = 0.0
	else:
		_hold_timer = 0.0


func _on_enter(body: Node2D) -> void:
	if not body.is_in_group(player_group): return
	_focused_body = body; _hold_timer = 0.0
	focused.emit(body)


func _on_exit(body: Node2D) -> void:
	if body != _focused_body: return
	unfocused.emit(body)
	_focused_body = null; _hold_timer = 0.0


func get_focused_body() -> Node2D: return _focused_body
