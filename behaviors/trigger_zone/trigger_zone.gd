## TriggerZone — Zona de Gatilho | Godot 4.7.
##
## Area2D com sinais zone_entered/zone_exited. Filtro por grupo,
## trigger_once desativa após primeiro uso. Auto-cria CollisionShape2D.
##
## @behavior: trigger_zone
## @genres: generic
## @tutorial: behaviors/trigger_zone/README.md

@tool
class_name TriggerZone
extends Area2D

@export var trigger_group: String = ""
@export var trigger_once: bool = false
@export var shape_size: Vector2 = Vector2(64, 64):
	set(v): shape_size = Vector2(maxf(v.x, 8), maxf(v.y, 8))

signal zone_entered(body: Node2D)
signal zone_exited(body: Node2D)

var _triggered: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_setup_shape()
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	_initialized = true


func _setup_shape() -> void:
	for child in get_children():
		if child is CollisionShape2D:
			return  # já tem
	var shape := CollisionShape2D.new(); shape.name = "TriggerShape"
	var rect := RectangleShape2D.new(); rect.size = shape_size
	shape.shape = rect; add_child(shape)


func _on_body_entered(body: Node2D) -> void:
	if _triggered and trigger_once: return
	if not _is_valid(body): return
	_triggered = true
	zone_entered.emit(body)
	if trigger_once:
		set_deferred("monitoring", false)


func _on_body_exited(body: Node2D) -> void:
	if not _is_valid(body): return
	zone_exited.emit(body)


func _is_valid(body: Node2D) -> bool:
	if trigger_group.is_empty(): return true
	return body.is_in_group(trigger_group)


## Reseta o estado triggered (reativa trigger_once).
func reset_trigger() -> void:
	_triggered = false
	monitoring = true
