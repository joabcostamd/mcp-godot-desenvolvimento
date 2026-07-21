## Tooltip — Dica Flutuante | Godot 4.7.
##
## Control que exibe tooltip ao passar o mouse no parent.
## Conecta mouse_entered/mouse_exited do parent automaticamente.
## Cria PanelContainer + Label internos para exibição.
##
## @behavior: tooltip
## @genres: generic
## @tutorial: behaviors/tooltip/README.md

@tool
class_name Tooltip
extends Control

## Texto exibido no tooltip.
@export var tooltip_text: String = ""

## Atraso antes de mostrar (0 = imediato).
@export var show_delay: float = 0.5:
	set(v):
		show_delay = clampf(v, 0.0, 5.0)
		if _delay_timer:
			_delay_timer.wait_time = show_delay

## Deslocamento em relação ao canto do parent (ou ao mouse).
@export var position_offset: Vector2 = Vector2(0, -40)

## Se true, segue o mouse; se false, posição fixa relativa ao parent.
@export var follow_mouse: bool = true

signal tooltip_shown()
signal tooltip_hidden()

var _panel: PanelContainer
var _label: Label
var _delay_timer: Timer
var _visible: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_create_ui()
	_connect_parent()
	_initialized = true


func _create_ui() -> void:
	# Timer de delay
	if not _delay_timer:
		_delay_timer = Timer.new()
		_delay_timer.name = "DelayTimer"
		_delay_timer.one_shot = true
		_delay_timer.wait_time = show_delay
		_delay_timer.timeout.connect(_show_panel)
		add_child(_delay_timer)

	# Painel de fundo
	_panel = PanelContainer.new()
	_panel.name = "TooltipPanel"
	_panel.visible = false
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE  # não bloqueia input
	add_child(_panel)

	# Label
	_label = Label.new()
	_label.name = "TooltipLabel"
	_label.text = tooltip_text
	_label.add_theme_font_size_override("font_size", 12)
	_panel.add_child(_label)

	# Z-order: acima de tudo
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _connect_parent() -> void:
	var parent := get_parent()
	if not parent or not parent is Control:
		return
	if not parent.mouse_entered.is_connected(_on_mouse_entered):
		parent.mouse_entered.connect(_on_mouse_entered)
	if not parent.mouse_exited.is_connected(_on_mouse_exited):
		parent.mouse_exited.connect(_on_mouse_exited)


func _on_mouse_entered() -> void:
	if tooltip_text.is_empty():
		return
	if show_delay <= 0.0:
		_show_panel()
	else:
		_delay_timer.start()


func _on_mouse_exited() -> void:
	_delay_timer.stop()
	_hide_panel()


func _show_panel() -> void:
	_label.text = tooltip_text
	_panel.visible = true
	_visible = true
	_update_position()
	tooltip_shown.emit()


func _hide_panel() -> void:
	_panel.visible = false
	_visible = false
	tooltip_hidden.emit()


func _update_position() -> void:
	if not _panel.visible:
		return

	var parent := get_parent()
	if not parent or not parent is Control:
		return

	if follow_mouse:
		_panel.global_position = _panel.get_global_mouse_position() + position_offset
	else:
		_panel.position = position_offset


func _process(_delta: float) -> void:
	if _visible and follow_mouse:
		_update_position()


## Mostra o tooltip manualmente (ignora delay e parent).
func show_tooltip(text: String = "") -> void:
	if not text.is_empty():
		tooltip_text = text
	if tooltip_text.is_empty():
		return
	_delay_timer.stop()
	_show_panel()


## Esconde o tooltip manualmente.
func hide_tooltip() -> void:
	_delay_timer.stop()
	_hide_panel()


## Retorna true se o tooltip está visível.
func is_visible_tooltip() -> bool:
	return _visible
