## Node que move a Camera2D parent ao longo de um Path2D child.
## Generos: platformer, generic.
## Tags: camera, path.
## Extends: Node.
## Sinais: waypoint_reached(), path_completed().
## Dependencias: nenhuma.
## @behavior: camera_path
@tool class_name CameraPath extends Node
@export var speed: float = 100.0: set(v): speed=clampf(v,1.0,1000.0)
@export var loop: bool = false
signal waypoint_reached(index: int)
signal path_completed()
var _camera: Camera2D = null
var _path: Path2D = null
var _path_follow: PathFollow2D = null
var _progress: float = 0.0
var _last_waypoint: int = -1
var _moving: bool = false
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	var p:=get_parent()
	if p is Camera2D: _camera=p as Camera2D
	for c in get_children():
		if c is Path2D and not _path: _path=c as Path2D
	if _path: _path_follow=PathFollow2D.new(); _path.add_child(_path_follow)
	_initialized=true
func _process(delta: float) -> void:
	if not _moving or not _path_follow or not _camera: return
	_progress+=speed*delta
	var path_len:=_path.curve.get_baked_length()
	if path_len<=0: return
	if _progress>=path_len:
		if loop: _progress=fmod(_progress,path_len)
		else: _progress=path_len; _moving=false; path_completed.emit(); return
	_path_follow.progress=_progress
	_camera.global_position=_path_follow.global_position
	var wp:=_get_current_waypoint()
	if wp!=_last_waypoint: _last_waypoint=wp; waypoint_reached.emit(wp)
func start() -> void: _progress=0.0; _last_waypoint=-1; _moving=true
func stop() -> void: _moving=false
func _get_current_waypoint() -> int:
	if not _path or not _path.curve: return -1
	var c:=_path.curve; var bc:=c.get_baked_points()
	for i in bc.size():
		if c.get_closest_offset(bc[i])>=_progress: return i
	return bc.size()-1
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not _camera: w.append("Parent não é Camera2D.")
	if not _path: w.append("Nenhum Path2D child encontrado.")
	return w
