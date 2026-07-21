## ParallaxBackground — Fundo com Paralaxe | Godot 4.7.
@tool
class_name ParallaxBackground
extends Node2D

@export var auto_scroll: Vector2 = Vector2.ZERO
@export var follow_camera: bool = true

var _layers: Array[Dictionary] = []
var _camera: Camera2D = null
var _last_camera_pos: Vector2 = Vector2.ZERO
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	_scan_layers(); _initialized = true

func _scan_layers() -> void:
	for c in get_children():
		if c is Sprite2D:
			_layers.append({"sprite": c, "scroll_scale": (c as Sprite2D).get_meta("parallax_scale", 1.0)})

func _process(delta: float) -> void:
	if follow_camera: _find_camera()
	var cam_offset := Vector2.ZERO
	if _camera:
		cam_offset = _camera.global_position - _last_camera_pos
		_last_camera_pos = _camera.global_position
	for layer in _layers:
		var sprite := layer.sprite as Sprite2D
		if not sprite: continue
		var scale: float = layer.scroll_scale
		sprite.position -= cam_offset * (1.0 - scale)
		sprite.position += auto_scroll * scale * delta

func _find_camera() -> void:
	if _camera and is_instance_valid(_camera): return
	var viewport := get_viewport()
	if viewport: _camera = viewport.get_camera_2d()

func add_layer(texture: Texture2D, scroll_scale: float = 1.0) -> void:
	var s := Sprite2D.new(); s.texture = texture; s.set_meta("parallax_scale", scroll_scale)
	add_child(s); _layers.append({"sprite": s, "scroll_scale": scroll_scale})
