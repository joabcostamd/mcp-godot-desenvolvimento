## Trail — Rastro Visual | Godot 4.7 Style Guide compliant.
##
## Line2D que segue o nó pai, acumulando pontos históricos.
## _process adiciona pontos com spacing configurável.
## Fade opcional via modulate.a nos pontos.
##
## @behavior: trail
## @genres: generic
## @tutorial: behaviors/trail/README.md

@tool
class_name Trail
extends Line2D

@export var max_points: int = 20: set(v): max_points = clampi(v, 2, 200)
@export var point_spacing: float = 5.0: set(v): point_spacing = clampf(v, 1, 100)
@export var fade: bool = true
@export var trail_width: float = 3.0: set(v): trail_width = clampf(v, 0.5, 50)

var _points: Array[Vector2] = []  # histórico em coordenadas globais
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	width = trail_width
	clear_points()
	_initialized = true


func _process(_delta: float) -> void:
	var parent := get_parent()
	if not parent or not parent is Node2D:
		return

	var global_pos := (parent as Node2D).global_position

	# Adiciona ponto se distância > spacing (ou lista vazia)
	if _points.is_empty() or global_pos.distance_to(_points.back()) >= point_spacing:
		_points.append(global_pos)

		# Limita tamanho
		while _points.size() > max_points:
			_points.pop_front()

	# Reconstrói Line2D
	var local_points: Array[Vector2] = []
	for gp in _points:
		local_points.append(to_local(gp))

	points = PackedVector2Array(local_points)

	# Aplica fading via gradient (se habilitado)
	if fade and _points.size() > 1:
		gradient = _build_fade_gradient(_points.size())


func _build_fade_gradient(point_count: int) -> Gradient:
	var g := Gradient.new()
	var c0 := Color(default_color, 0.0)
	var c1 := default_color
	g.set_color(0, c0)
	g.set_color(1, c1)
	return g


## Limpa o trail completamente.
func clear() -> void:
	_points.clear()
	clear_points()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
