## Node que controla zoom contínuo da Camera2D com limites min/max e velocidade.
## Generos: generic.
## Tags: camera, zoom.
## Extends: Node.
## Sinais: zoomed().
## Dependencias: nenhuma.
## @behavior: camera_zoom_range
@tool class_name CameraZoomRange extends Node
@export var zoom_min: Vector2 = Vector2(0.5,0.5): set(v)=zoom_min=Vector2(clampf(v.x,0.1,10),clampf(v.y,0.1,10))
@export var zoom_max: Vector2 = Vector2(3.0,3.0): set(v)=zoom_max=Vector2(clampf(v.x,0.1,10),clampf(v.y,0.1,10))
@export var zoom_speed: float = 2.0: set(v)=zoom_speed=clampf(v,0.1,10.0)
signal zoomed(new_zoom: Vector2)
var _camera: Camera2D = null
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	var p:=get_parent()
	if p is Camera2D: _camera=p as Camera2D
	_initialized=true
func _process(delta: float) -> void:
	if not _camera: return
	var z:=_camera.zoom
	if Input.is_action_pressed("ui_accept"): z+=Vector2.ONE*zoom_speed*delta
	if Input.is_action_pressed("ui_cancel"): z-=Vector2.ONE*zoom_speed*delta
	z=Vector2(clampf(z.x,zoom_min.x,zoom_max.x),clampf(z.y,zoom_min.y,zoom_max.y))
	if _camera.zoom!=z: _camera.zoom=z; zoomed.emit(z)
func zoom_in() -> void: _apply_zoom(zoom_speed*0.1)
func zoom_out() -> void: _apply_zoom(-zoom_speed*0.1)
func _apply_zoom(delta: float) -> void:
	if not _camera: return
	var z:=_camera.zoom+Vector2.ONE*delta
	z=Vector2(clampf(z.x,zoom_min.x,zoom_max.x),clampf(z.y,zoom_min.y,zoom_max.y))
	_camera.zoom=z; zoomed.emit(z)
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not _camera: w.append("Parent nao eh Camera2D.")
	return w
