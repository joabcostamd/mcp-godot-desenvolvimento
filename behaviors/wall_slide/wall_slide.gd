## WallSlide — Deslize em Parede | Godot 4.7.
##
## Node filho de CharacterBody2D. Detecta paredes com RayCast2D
## esquerdo/direito. Reduz velocidade de queda durante slide.
## Wall jump: ui_accept na parede impulsiona para o lado oposto.
##
## @behavior: wall_slide
## @genres: platformer, metroidvania, generic
## @tutorial: behaviors/wall_slide/README.md

@tool
class_name WallSlide
extends Node

## Velocidade máxima de descida na parede (px/s).
@export var slide_speed: float = 60.0:
	set(v): slide_speed = clampf(v, 10.0, 500.0)

## Força horizontal do wall jump (px/s).
@export var wall_jump_horizontal: float = 300.0:
	set(v): wall_jump_horizontal = clampf(v, 50.0, 1000.0)

## Força vertical do wall jump (negativa = para cima).
@export var wall_jump_vertical: float = -350.0:
	set(v): wall_jump_vertical = clampf(v, -2000.0, -50.0)

## Distância de detecção da parede (px).
@export var wall_detection_distance: float = 16.0:
	set(v): wall_detection_distance = clampf(v, 4.0, 64.0)

## Se false, não processa wall slide/jump.
@export var enabled: bool = true

signal wall_sliding(is_sliding: bool)
signal wall_jumped(direction: Vector2)

var _ray_left: RayCast2D
var _ray_right: RayCast2D
var _is_sliding: bool = false
var _wall_dir: int = 0  # -1 = esquerda, 1 = direita, 0 = nenhuma
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_create_rays()
	_initialized = true


func _create_rays() -> void:
	if _ray_left:
		return

	_ray_left = RayCast2D.new()
	_ray_left.name = "WallRayLeft"
	_ray_left.target_position = Vector2(-wall_detection_distance, 0)
	_ray_left.enabled = false  # ativamos manualmente
	add_child(_ray_left)

	_ray_right = RayCast2D.new()
	_ray_right.name = "WallRayRight"
	_ray_right.target_position = Vector2(wall_detection_distance, 0)
	_ray_right.enabled = false
	add_child(_ray_right)


func _physics_process(_delta: float) -> void:
	if not enabled:
		return

	var parent := get_parent()
	if not parent is CharacterBody2D:
		return

	var body := parent as CharacterBody2D

	# Não processa no chão
	if body.is_on_floor():
		if _is_sliding:
			_is_sliding = false
			_wall_dir = 0
			wall_sliding.emit(false)
		return

	# Detecta paredes
	_ray_left.target_position = Vector2(-wall_detection_distance, 0)
	_ray_right.target_position = Vector2(wall_detection_distance, 0)
	_ray_left.force_raycast_update()
	_ray_right.force_raycast_update()

	var on_left := _ray_left.is_colliding()
	var on_right := _ray_right.is_colliding()

	if on_left and not on_right:
		_wall_dir = -1
	elif on_right and not on_left:
		_wall_dir = 1
	else:
		_wall_dir = 0

	# Wall slide
	if _wall_dir != 0:
		if not _is_sliding:
			_is_sliding = true
			wall_sliding.emit(true)
		# Limita velocidade de queda
		body.velocity.y = minf(body.velocity.y, slide_speed)

		# Wall jump
		if Input.is_action_just_pressed("ui_accept"):
			body.velocity.x = wall_jump_horizontal * (-_wall_dir)
			body.velocity.y = wall_jump_vertical
			var dir := Vector2(float(-_wall_dir), -1.0)
			wall_jumped.emit(dir)
			_is_sliding = false
			_wall_dir = 0
			wall_sliding.emit(false)
	else:
		if _is_sliding:
			_is_sliding = false
			_wall_dir = 0
			wall_sliding.emit(false)


## Retorna true se está deslizando na parede.
func is_wall_sliding() -> bool:
	return _is_sliding


## Retorna a direção da parede (-1=esquerda, 1=direita, 0=nenhuma).
func get_wall_direction() -> int:
	return _wall_dir
