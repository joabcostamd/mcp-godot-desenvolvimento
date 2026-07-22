## FloatingText — Texto Flutuante | Godot 4.7 Style Guide compliant.
##
## Exibe texto que sobe verticalmente e desaparece com fade.
## show_text(text, color) dispara a animação. Sinal text_shown ao terminar.
##
## @behavior: floating_text
## @genres: generic
## @tutorial: behaviors/floating_text/README.md

@tool
class_name FloatingText
extends Node2D

@export var speed: float = 100.0: set(v): speed = clampf(v, 10, 500)
@export var lifetime: float = 1.0: set(v): lifetime = clampf(v, 0.1, 5)
@export var fade_duration: float = 0.3: set(v): fade_duration = clampf(v, 0, 2)
@export var font_size: int = 24: set(v): font_size = clampi(v, 8, 128)
@export var outline_size: int = 2: set(v): outline_size = clampi(v, 0, 10)

signal text_shown()

var _label: Label = null
var _tween: Tween = null
var _elapsed: float = 0.0
var _active: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_setup_label()
	_initialized = true


func _setup_label() -> void:
	_label = Label.new()
	_label.name = "FloatingLabel"
	_label.add_theme_font_size_override("font_size", font_size)
	if outline_size > 0:
		_label.add_theme_color_override("font_outline_color", Color.BLACK)
		_label.add_theme_constant_override("outline_size", outline_size)
	add_child(_label)


## Exibe texto flutuante. Retorna false se já estiver ativo.
func show_text(txt: String, clr: Color = Color.WHITE) -> bool:
	if _active:
		return false
	if not _label:
		_setup_label()

	_label.text = txt
	_label.add_theme_color_override("font_color", clr)
	_label.modulate.a = 1.0
	_label.position = Vector2.ZERO

	_active = true
	_elapsed = 0.0

	# Tween de fade-out no final
	if fade_duration > 0.0 and lifetime > fade_duration:
		_kill_tween()
		_tween = create_tween()
		_tween.tween_interval(lifetime - fade_duration)
		_tween.tween_property(_label, "modulate:a", 0.0, fade_duration)

	return true


func _process(delta: float) -> void:
	if not _active:
		return

	_elapsed += delta

	if _elapsed >= lifetime:
		_finish()
		return

	# Move para cima
	position.y -= speed * delta


func _finish() -> void:
	_active = false
	_kill_tween()
	text_shown.emit()
	queue_free()


func _kill_tween() -> void:
	if _tween and is_instance_valid(_tween):
		_tween.kill()
	_tween = null


func is_active() -> bool:
	return _active


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
