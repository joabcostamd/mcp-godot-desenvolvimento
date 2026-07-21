## Projectile — Projétil Linear | Godot 4.7 Style Guide compliant.
##
## Area2D que se move em linha reta, causa dano ao colidir e se autodestroi.
## Componente plugável: instancie como filho de um spawner ou arma.
##
## @behavior: projectile
## @genres: topdown_shooter, platformer, bullet_hell, roguelike, tower_defense,
##          metroidvania, generic
## @tutorial: behaviors/projectile/README.md

@tool
class_name Projectile
extends Area2D

## Velocidade de movimento (px/s).
@export var speed: float = 400.0

## Dano causado ao atingir um alvo com Health.
@export var damage: int = 10

## Tempo máximo de vida (0 = infinito).
@export var lifetime: float = 5.0

## Distância máxima percorrida (0 = infinito).
@export var max_distance: float = 1000.0

## Se true, atravessa alvos sem se destruir.
@export var piercing: bool = false

## Emitido ao atingir algo.
signal hit(target: Node, damage_dealt: int)

## Emitido quando o projétil expira.
signal expired()

var _direction: Vector2 = Vector2.RIGHT
var _distance_traveled: float = 0.0
var _lifetime_elapsed: float = 0.0
var _spawn_position: Vector2
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_spawn_position = global_position
	if lifetime <= 0.0 and max_distance <= 0.0:
		push_warning("[Projectile] lifetime e max_distance são 0 — projétil nunca expira.")
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)
	_initialized = true


func _physics_process(delta: float) -> void:
	# Movimento
	var step := _direction * speed * delta
	global_position += step
	_distance_traveled += step.length()

	# Expiração por tempo
	if lifetime > 0.0:
		_lifetime_elapsed += delta
		if _lifetime_elapsed >= lifetime:
			_expire()
			return

	# Expiração por distância
	if max_distance > 0.0 and _distance_traveled >= max_distance:
		_expire()
		return


## Define a direção do projétil. Chamado pelo spawner.
func set_direction(dir: Vector2) -> void:
	_direction = dir.normalized()
	# Rotaciona o projétil para apontar na direção
	rotation = _direction.angle()


## Define o alvo e calcula a direção automaticamente.
func set_target(target: Node2D) -> void:
	if target:
		set_direction(target.global_position - global_position)


func _on_body_entered(body: Node2D) -> void:
	_handle_hit(body)


func _on_area_entered(area: Area2D) -> void:
	_handle_hit(area)


func _handle_hit(target: Node) -> void:
	# Tenta causar dano se o alvo tem um componente Health
	var health := _find_health(target)
	var damage_dealt := 0

	if health and is_instance_valid(health):
		damage_dealt = health.take_damage(damage)

	hit.emit(target, damage_dealt)

	if not piercing:
		queue_free()


func _expire() -> void:
	expired.emit()
	queue_free()


## Procura por um componente Health no nó alvo ou nos pais.
func _find_health(node: Node) -> Health:
	# Busca no próprio nó
	if node is Health:
		return node
	# Busca nos filhos diretos
	for child in node.get_children():
		if child is Health:
			return child
	# Busca no pai (para cases onde a colisão é com um CollisionShape2D)
	var parent := node.get_parent()
	if parent and parent is Health:
		return parent
	return null


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("Consider setting collision_mask to detect specific layers.")
	return w
