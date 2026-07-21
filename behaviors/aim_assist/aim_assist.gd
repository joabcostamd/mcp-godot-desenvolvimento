## Behavior Aim Assist para Godot 4.
## Generos: shooter.
## Tags: input.
## Extends: Node.
## Sinais: assist_activated().
## Dependencias: nenhuma.
## @behavior: aim_assist
@tool class_name AimAssist extends Node
@export var friction: float = 0.3: set(v)=friction=clampf(v,0.0,1.0)
@export var magnetism: float = 0.5: set(v)=magnetism=clampf(v,0.0,1.0)
@export var assist_radius: float = 200.0: set(v)=assist_radius=clampf(v,10.0,1000.0)
signal assist_activated()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func get_assisted_aim(cursor_pos: Vector2, targets: Array[Node2D]) -> Vector2:
	var best: Node2D = null; var best_dist:=assist_radius
	for t in targets:
		var d:=cursor_pos.distance_to(t.global_position)
		if d<best_dist: best_dist=d; best=t
	if best: assist_activated.emit(); return cursor_pos.lerp(best.global_position,magnetism)
	return cursor_pos
func _get_configuration_warnings() -> PackedStringArray: return []
