## Node que adiciona avoidance (desvio de obstáculos) ao parent CharacterBody2D.
## Generos: topdown_shooter, rpg, generic.
## Tags: navegacao, ai.
## Extends: Node.
## Dependencias: pathfinding.
## @behavior: avoidance
@tool
class_name Avoidance
extends Node

@export var radius: float = 32.0: set(v): radius=clampf(v,4,128); _update_agent()
@export var priority: float = 1.0: set(v): priority=clampf(v,0,10); _update_agent()
@export var max_speed: float = 200.0: set(v): max_speed=clampf(v,10,2000); _update_agent()

var _agent: NavigationAgent2D
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_agent = NavigationAgent2D.new(); _agent.name = "AvoidAgent"
	_agent.avoidance_enabled = true; _update_agent()
	add_child(_agent); _initialized = true

func _update_agent() -> void:
	if not _agent: return
	_agent.radius = radius; _agent.avoidance_priority = priority
	_agent.max_speed = max_speed

func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not get_parent() is CharacterBody2D: w.append("Parent must be CharacterBody2D.")
	return w
