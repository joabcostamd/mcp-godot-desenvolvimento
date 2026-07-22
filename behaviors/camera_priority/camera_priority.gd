## Node que ativa automaticamente a Camera2D parent quando ela tem a maior prioridade entre câmeras irmãs.
## Generos: platformer, generic.
## Tags: camera, prioridade.
## Extends: Node.
## Sinais: camera_activated().
## Dependencias: nenhuma.
## @behavior: camera_priority
@tool class_name CameraPriority extends Node
@export var priority: int = 0: set(v): priority=clampi(v,0,100)
@export var transition_duration: float = 0.5: set(v): transition_duration=clampf(v,0.0,5.0)
signal camera_activated()
var _camera: Camera2D = null
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	var p:=get_parent()
	if p is Camera2D: _camera=p as Camera2D
	_evaluate_priority()
	_initialized=true
func _evaluate_priority() -> void:
	if not _camera: return
	var siblings:=_camera.get_parent().get_children() if _camera.get_parent() else []
	var best: Camera2D = null; var best_prio:=-1
	for s in siblings:
		if s is Camera2D:
			var cp:=_find_priority_on(s)
			var prio:=cp.priority if cp else 0
			if prio>best_prio: best_prio=prio; best=s as Camera2D
	if best==_camera and not _camera.enabled:
		_camera.enabled=true; camera_activated.emit()
func _find_priority_on(node: Node) -> CameraPriority:
	for c in node.get_children():
		if c is CameraPriority: return c as CameraPriority
	return null
func activate() -> void:
	priority=100
	for s in (_camera.get_parent().get_children() if _camera.get_parent() else []):
		if s is Camera2D and s!=_camera:
			var cp:=_find_priority_on(s)
			if cp and cp.priority>=priority: cp.priority=priority-1
	_evaluate_priority()
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not _camera: w.append("Parent não é Camera2D.")
	return w
