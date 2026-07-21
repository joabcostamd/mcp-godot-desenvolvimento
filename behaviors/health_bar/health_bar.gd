## HealthBar — Barra de Vida | Godot 4.7.
##
## Node2D + ColorRect que espelha current_hp/max_hp do Health alvo.
## target_health: caminho ou busca sibling automaticamente.
##
## @behavior: health_bar
## @genres: generic

@tool
class_name HealthBar
extends Node2D

@export var target_health: NodePath = NodePath()
@export var bar_color: Color = Color.RED
@export var background_color: Color = Color(0.2, 0.2, 0.2, 1)
@export var show_text: bool = false
@export var smooth: bool = true
@export var bar_width: float = 100.0: set(v): bar_width = clampf(v, 10, 1000)
@export var bar_height: float = 12.0: set(v): bar_height = clampf(v, 4, 200)

var _health: Health = null
var _bg: ColorRect = null
var _fill: ColorRect = null
var _label: Label = null
var _display_ratio: float = 1.0
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_setup_visuals()
	_find_health()
	_initialized = true


func _setup_visuals() -> void:
	_bg = ColorRect.new(); _bg.name = "Background"
	_bg.color = background_color; _bg.size = Vector2(bar_width, bar_height)
	add_child(_bg)

	_fill = ColorRect.new(); _fill.name = "Fill"
	_fill.color = bar_color; _fill.size = Vector2(bar_width, bar_height)
	add_child(_fill)

	if show_text:
		_label = Label.new(); _label.name = "HPLabel"
		_label.add_theme_font_size_override("font_size", 10)
		_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_label.size = Vector2(bar_width, bar_height)
		add_child(_label)


func _find_health() -> void:
	if target_health and not target_health.is_empty():
		_health = get_node(target_health) as Health
	else:
		var parent := get_parent()
		if parent:
			for child in parent.get_children():
				if child is Health:
					_health = child; break


func _process(delta: float) -> void:
	if not _health: return
	var ratio := float(_health.current_hp) / float(_health.max_hp)
	if smooth:
		_display_ratio = lerpf(_display_ratio, ratio, delta * 10.0)
	else:
		_display_ratio = ratio

	if _fill:
		_fill.size.x = bar_width * _display_ratio
		_fill.color = bar_color

	if _label:
		_label.text = "%d / %d" % [_health.current_hp, _health.max_hp]


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
