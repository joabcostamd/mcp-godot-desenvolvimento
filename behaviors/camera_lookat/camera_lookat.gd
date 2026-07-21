@tool class_name CameraLookat extends Node
@export var target: NodePath: set(v)=target=v
@export var look_offset: Vector2 = Vector2.ZERO
@export var damping: float = 0.1: set(v)=damping=clampf(v,0.01,1.0)
var _camera: Camera2D = null
var _target_node: Node2D = null
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	var p:=get_parent()
	if p is Camera2D: _camera=p as Camera2D
	_resolve_target()
	_initialized=true
func _resolve_target() -> void:
	if target.is_empty(): return
	_target_node=get_node_or_null(target) as Node2D
func _process(_delta: float) -> void:
	if not _camera or not _target_node: return
	var desired:=_target_node.global_position+look_offset
	_camera.global_position=_camera.global_position.lerp(desired,damping)
func set_target_node(node: Node2D) -> void: _target_node=node
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not _camera: w.append("Parent não é Camera2D.")
	if not _target_node: w.append("Target não definido ou inválido.")
	return w
