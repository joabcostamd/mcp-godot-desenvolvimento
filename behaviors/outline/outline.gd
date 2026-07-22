## Outline — Contorno Visual | Godot 4.7.
##
## Node que aplica outline ao parent CanvasItem via shader material.
## Cor, largura e show_on_focus configuráveis.

@tool
class_name Outline
extends Node

@export var outline_color: Color = Color.WHITE:
	set(v):
		outline_color = v
		if _material: _material.set_shader_parameter("color", v)
@export var outline_width: float = 2.0:
	set(v):
		outline_width = clampf(v, 1, 10)
		if _material: _material.set_shader_parameter("width", v)
@export var show_on_focus: bool = false

var _material: ShaderMaterial = null
var _outline_visible: bool = true
var _initialized: bool = false

const SHADER := preload("res://behaviors/outline/outline.gdshader")


func _ready() -> void:
	if _initialized: return
	_setup_outline()
	_initialized = true


func _setup_outline() -> void:
	var parent := get_parent()
	if not parent is CanvasItem: return

	_material = ShaderMaterial.new()
	_material.shader = SHADER
	_material.set_shader_parameter("color", outline_color)
	_material.set_shader_parameter("width", outline_width)

	(parent as CanvasItem).material = _material


func show_outline() -> void:
	var parent := get_parent()
	if not parent is CanvasItem or not _material: return
	_material.set_shader_parameter("enabled", true)


func hide_outline() -> void:
	if not _material: return
	_material.set_shader_parameter("enabled", false)


func is_outline_visible() -> bool:
	if not _material: return false
	return _material.get_shader_parameter("enabled") as bool


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
