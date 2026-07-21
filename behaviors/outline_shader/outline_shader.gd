@tool class_name OutlineShader extends Node
@export var outline_color: Color = Color(0,1,1,1): set(v): outline_color=v; _update()
@export var outline_width: float = 1.0: set(v): outline_width=clampf(v,0,5); _update()
var _material: ShaderMaterial; var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	var p:=get_parent(); if not p is CanvasItem: return
	_material=ShaderMaterial.new(); _material.shader=preload("res://behaviors/outline_shader/outline_shader.gdshader")
	(p as CanvasItem).material=_material; _update(); _initialized=true

func _update() -> void:
	if _material: _material.set_shader_parameter("outline_color",outline_color)
	if _material: _material.set_shader_parameter("outline_width",outline_width)
