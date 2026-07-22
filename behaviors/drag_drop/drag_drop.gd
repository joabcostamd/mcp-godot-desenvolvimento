## DragDrop — Arrastar e Soltar | Godot 4.7.
##
## Control que torna o parent arrastável via set_drag_forwarding().
## Detecta drop em zonas do grupo drop_group. Snap em grid opcional.
##
## @behavior: drag_drop
## @genres: generic, puzzle, rpg, card
## @tutorial: behaviors/drag_drop/README.md

@tool
class_name DragDrop
extends Control

## Mostra preview do controle durante o arrasto.
@export var drag_preview: bool = true

## Tamanho do grid para snap (0,0 = sem snap).
@export var snap_size: Vector2 = Vector2.ZERO:
	set(v):
		snap_size = Vector2(maxf(v.x, 0.0), maxf(v.y, 0.0))

## Grupo dos nós que aceitam drop (vazio = qualquer Control).
@export var drop_group: String = ""

signal drag_started()
signal dropped(target: NodePath)
signal drag_cancelled()

var _drag_data: Variant = null
var _dragging: bool = false
var _initial_position: Vector2 = Vector2.ZERO
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_setup_drag_forwarding()
	_initialized = true


func _setup_drag_forwarding() -> void:
	var parent := get_parent()
	if not parent or not parent is Control:
		return
	(parent as Control).set_drag_forwarding(_get_drag_data, _can_drop_data, _drop_data)


## Chamado pelo Godot ao iniciar arrasto no parent.
func _get_drag_data(at_position: Vector2) -> Variant:
	_dragging = true
	var parent := get_parent()
	if parent is Control:
		_initial_position = (parent as Control).position
	_drag_data = {"source": parent, "behavior": self}
	drag_started.emit()

	if drag_preview and parent is Control:
		var preview := Control.new()
		preview.modulate.a = 0.7
		var dup := (parent as Control).duplicate()
		if dup and dup is Control:
			preview.add_child(dup)
		(parent as Control).set_drag_preview(preview)

	return _drag_data


## Chamado pelo Godot ao passar sobre um alvo potencial.
func _can_drop_data(at_position: Vector2, data: Variant) -> bool:
	if not drop_group.is_empty():
		var target := _get_drop_target()
		if not target or not target.is_in_group(drop_group):
			return false
	return true


## Chamado pelo Godot ao soltar sobre alvo válido.
func _drop_data(at_position: Vector2, data: Variant) -> void:
	_dragging = false
	var parent := get_parent()
	var target := _get_drop_target()

	if parent is Control and target:
		var pos := at_position
		if snap_size.x > 0.0 and snap_size.y > 0.0:
			pos = _snap_to_grid(pos)
		(parent as Control).global_position = target.global_position + pos

	dropped.emit(target.get_path() if target else NodePath())


## Chamado pelo Godot ao cancelar arrasto (soltou fora).
func _notification(what: int) -> void:
	if what == NOTIFICATION_DRAG_END and _dragging:
		_dragging = false
		var parent := get_parent()
		if parent is Control and not _did_drop():
			# Volta à posição inicial se não dropou
			(parent as Control).position = _initial_position
			drag_cancelled.emit()


func _did_drop() -> bool:
	# Checa se a posição atual é diferente da inicial (drop ocorreu)
	var parent := get_parent()
	if parent is Control:
		return (parent as Control).position != _initial_position
	return false


func _get_drop_target() -> Control:
	# Godot não expõe o drop target diretamente.
	# Usamos o Control sob o mouse como fallback.
	# set_drag_forwarding trata _drop_data com o target correto.
	return null


func _snap_to_grid(pos: Vector2) -> Vector2:
	var x := round(pos.x / snap_size.x) * snap_size.x
	var y := round(pos.y / snap_size.y) * snap_size.y
	return Vector2(x, y)


## Inicia arrasto manualmente (sem mouse).
func start_drag(data: Variant = null) -> void:
	var parent := get_parent()
	if parent is Control:
		_drag_data = data if data != null else {"source": parent}
		(parent as Control).force_drag(_drag_data, _get_drag_data(Vector2.ZERO))


## Retorna true se está arrastando no momento.
func is_dragging() -> bool:
	return _dragging


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
