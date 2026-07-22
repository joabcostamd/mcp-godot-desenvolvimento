## Node que aplica efeito de dissolução via shader ao parent CanvasItem.
## Generos: generic.
## Tags: shader, visual.
## Extends: Node.
## Sinais: dissolve_finished().
## Dependencias: nenhuma.
## @behavior: dissolve
@tool class_name Dissolve extends Node
@export var edge_color: Color = Color(1,0.5,0,1): set(v): edge_color=v; _update()
@export var edge_width: float = 0.1: set(v): edge_width=clampf(v,0,0.5); _update()
signal dissolve_finished()
var _material: ShaderMaterial; var _progress: float = 0.0; var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	var p:=get_parent(); if not p is CanvasItem: return
	_material=ShaderMaterial.new(); _material.shader=preload("res://behaviors/dissolve/dissolve.gdshader")
	_material.set_shader_parameter("edge_color",edge_color)
	_material.set_shader_parameter("edge_width",edge_width)
	_material.set_shader_parameter("progress",0.0)
	(p as CanvasItem).material=_material; _initialized=true

func set_progress(p: float) -> void:
	_progress=clampf(p,0,1); _update()
	if _progress>=1.0: dissolve_finished.emit()

func _update() -> void:
	if _material: _material.set_shader_parameter("progress",_progress)
	if _material: _material.set_shader_parameter("edge_color",edge_color)
	if _material: _material.set_shader_parameter("edge_width",edge_width)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	var p := get_parent()
	if not p is CanvasItem:
		w.append("Parent must be CanvasItem (Sprite2D, Control, etc.) for shader to apply.")
	return w
