## CameraFramed — Câmera com Dead Zone | Godot 4.7.
##
## Câmera que só segue o alvo quando ele sai da dead zone central.
## Movimento suave com damping na soft zone. Inspirado no
## Phantom Camera "Framed" — ideal para jogos de plataforma e ação.
##
## @behavior: camera_framed
## @genres: platformer, topdown_shooter, generic
## @tutorial: behaviors/camera_framed/README.md

@tool
class_name CameraFramed
extends Node

## Tamanho da zona morta central (target livre sem mover câmera).
@export var dead_zone: Vector2 = Vector2(100.0, 60.0):
	set(v):
		dead_zone = Vector2(clampf(v.x, 10.0, 2000.0), clampf(v.y, 10.0, 2000.0))

## Margem adicional além da dead zone onde a câmera segue com damping.
@export var soft_zone: Vector2 = Vector2(80.0, 50.0):
	set(v):
		soft_zone = Vector2(clampf(v.x, 0.0, 1000.0), clampf(v.y, 0.0, 1000.0))

## Fator de suavização (0.01 = muito lento, 1.0 = snap instantâneo).
@export var damping: float = 0.1:
	set(v):
		damping = clampf(v, 0.01, 1.0)

## Nó alvo a ser seguido. Se vazio, tenta encontrar no parent.
@export var target: Node2D = null

signal target_entered_dead_zone()

var _camera: Camera2D = null
var _was_in_dead_zone: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_camera()
	_initialized = true


func _find_camera() -> void:
	var p := get_parent()
	if p is Camera2D:
		_camera = p as Camera2D


func _process(_delta: float) -> void:
	if not _camera or not target:
		return

	var cam_pos := _camera.global_position
	var target_pos := target.global_position
	var delta_pos := target_pos - cam_pos

	var half_dead := dead_zone / 2.0
	var half_total := (dead_zone + soft_zone) / 2.0

	# Verifica se o target está dentro da dead zone
	var abs_dx := absf(delta_pos.x)
	var abs_dy := absf(delta_pos.y)

	var in_dead_x := abs_dx <= half_dead.x
	var in_dead_y := abs_dy <= half_dead.y
	var in_dead_zone := in_dead_x and in_dead_y

	if in_dead_zone:
		if not _was_in_dead_zone:
			target_entered_dead_zone.emit()
		_was_in_dead_zone = true
		return  # câmera parada

	_was_in_dead_zone = false

	# Calcula o deslocamento desejado da câmera
	var desired := Vector2.ZERO

	if abs_dx > half_dead.x:
		var overflow_x := abs_dx - half_dead.x
		var max_overflow_x := half_total.x - half_dead.x
		var t_x := clampf(overflow_x / max_overflow_x, 0.0, 1.0) if max_overflow_x > 0.0 else 1.0
		desired.x = signf(delta_pos.x) * overflow_x * t_x

	if abs_dy > half_dead.y:
		var overflow_y := abs_dy - half_dead.y
		var max_overflow_y := half_total.y - half_dead.y
		var t_y := clampf(overflow_y / max_overflow_y, 0.0, 1.0) if max_overflow_y > 0.0 else 1.0
		desired.y = signf(delta_pos.y) * overflow_y * t_y

	# Aplica damping: move a câmera suavemente
	var move := desired * damping
	_camera.global_position += move


## Define o alvo da câmera programaticamente.
func set_target(new_target: Node2D) -> void:
	target = new_target


## Retorna true se o alvo está dentro da dead zone.
func is_target_in_dead_zone() -> bool:
	if not _camera or not target:
		return false
	var delta_pos := target.global_position - _camera.global_position
	return absf(delta_pos.x) <= dead_zone.x / 2.0 and absf(delta_pos.y) <= dead_zone.y / 2.0


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not _camera:
		w.append("Nenhuma Camera2D detectada no parent — adicione como filho de Camera2D.")
	if not target:
		w.append("Nenhum target definido — câmera não seguirá nenhum nó.")
	return w
