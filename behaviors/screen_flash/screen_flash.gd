## ScreenFlash — Flash de Tela | Godot 4.7 Style Guide compliant.
##
## Exibe um ColorRect fullscreen com fade-in/out sobre CanvasLayer.
## flash(color, duration) dispara a animação. Sinal flashed ao terminar.
##
## @behavior: screen_flash
## @genres: generic
## @tutorial: behaviors/screen_flash/README.md

@tool
class_name ScreenFlash
extends CanvasLayer

@export var default_color: Color = Color.WHITE
@export var default_duration: float = 0.3: set(v): default_duration = clampf(v, 0.02, 5)
@export var fade_in: float = 0.05: set(v): fade_in = clampf(v, 0, 1)
@export var fade_out: float = 0.15: set(v): fade_out = clampf(v, 0, 1)

signal flashed()

var _rect: ColorRect = null
var _tween: Tween = null
var _active: bool = false
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_setup_rect()
	_initialized = true


func _setup_rect() -> void:
	_rect = ColorRect.new()
	_rect.name = "FlashRect"
	_rect.color = default_color
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Full rect anchors
	_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_rect.modulate.a = 0.0
	add_child(_rect)


## Dispara o flash. Se já estiver ativo, cancela o anterior e reinicia.
## color_override usa default_color se for Color.WHITE (transparente não faz sentido).
## duration_override < 0 usa default_duration.
func flash(color_override: Color = Color.WHITE, duration_override: float = -1.0) -> void:
	if not _rect:
		_setup_rect()

	var clr := color_override
	var dur := default_duration if duration_override < 0 else duration_override
	dur = maxf(dur, 0.02)

	# Cancela animação anterior
	_kill_tween()

	_rect.color = clr
	_rect.modulate.a = 0.0
	_active = true

	# Calcula hold time (tempo com tela totalmente opaca)
	var fi := minf(fade_in, dur * 0.4)
	var fo := minf(fade_out, dur * 0.4)
	var hold := dur - fi - fo
	if hold < 0:
		hold = 0.0
		fi = dur * 0.5
		fo = dur * 0.5

	_tween = create_tween()
	_tween.set_parallel(false)
	_tween.tween_property(_rect, "modulate:a", 1.0, fi)
	if hold > 0:
		_tween.tween_interval(hold)
	_tween.tween_property(_rect, "modulate:a", 0.0, fo)
	_tween.tween_callback(_on_flash_done)


func _on_flash_done() -> void:
	_active = false
	_tween = null
	if _rect:
		_rect.modulate.a = 0.0
	flashed.emit()


func _kill_tween() -> void:
	if _tween and is_instance_valid(_tween):
		_tween.kill()
	_tween = null


func is_active() -> bool:
	return _active
