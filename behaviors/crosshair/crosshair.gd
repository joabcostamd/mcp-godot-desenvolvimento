@tool
class_name Crosshair
extends Node2D

@export var crosshair_color: Color = Color.RED: set(v): crosshair_color=v; queue_redraw()
@export var crosshair_size: float = 16.0: set(v): crosshair_size=clampf(v,4,64); queue_redraw()
@export var crosshair_style: int = 0: set(v): crosshair_style=clampi(v,0,2); queue_redraw()
@export var gap: float = 4.0: set(v): gap=clampf(v,0,32); queue_redraw()
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_initialized = true

func _process(_delta: float) -> void:
	global_position = get_global_mouse_position()

func _draw() -> void:
	var s := crosshair_size; var g := gap
	if crosshair_style == 0:  # cross
		draw_line(Vector2(-s,0), Vector2(-g,0), crosshair_color, 2)
		draw_line(Vector2(g,0), Vector2(s,0), crosshair_color, 2)
		draw_line(Vector2(0,-s), Vector2(0,-g), crosshair_color, 2)
		draw_line(Vector2(0,g), Vector2(0,s), crosshair_color, 2)
	elif crosshair_style == 1:  # circle
		draw_arc(Vector2.ZERO, s*0.6, 0, TAU, 32, crosshair_color, 2)
		draw_line(Vector2(-s*0.3,0), Vector2(s*0.3,0), crosshair_color, 1)
		draw_line(Vector2(0,-s*0.3), Vector2(0,s*0.3), crosshair_color, 1)
	else:  # dot
		draw_circle(Vector2.ZERO, s*0.3, crosshair_color)

func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	return w
