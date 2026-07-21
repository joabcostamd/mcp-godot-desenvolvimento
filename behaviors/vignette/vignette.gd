## Vignette — Efeito Vinheta | Godot 4.7 Style Guide compliant.
##
## ColorRect fullscreen com GradientTexture2D radial sobre CanvasLayer.
## trigger(intensity, duration) com Tween em modulate.a.
##
## @behavior: vignette
## @genres: generic
## @tutorial: behaviors/vignette/README.md

@tool
class_name Vignette
extends CanvasLayer

@export var vignette_color: Color = Color.BLACK
@export var default_intensity: float = 0.5: set(v): default_intensity = clampf(v, 0, 1)
@export var default_duration: float = 0.5: set(v): default_duration = clampf(v, 0.1, 5)

signal vignette_started()
signal vignette_finished()

var _rect: ColorRect = null
var _tween: Tween = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_setup_rect()
	_initialized = true


func _setup_rect() -> void:
	_rect = ColorRect.new()
	_rect.name = "VignetteRect"
	_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_rect.modulate.a = 0.0

	var tex := GradientTexture2D.new()
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(0.5, 1.0)
	var grad := Gradient.new()
	grad.set_color(0, Color.TRANSPARENT)
	grad.set_color(1, vignette_color)
	tex.gradient = grad
	_rect.texture = tex

	add_child(_rect)


## Aplica vinheta com transição.
## intensity_override < 0 usa default_intensity.
func trigger(intensity_override: float = -1.0, duration_override: float = -1.0) -> void:
	if not _rect:
		_setup_rect()

	var intensity := default_intensity if intensity_override < 0 else intensity_override
	intensity = clampf(intensity, 0, 1)
	var dur := default_duration if duration_override < 0 else duration_override
	dur = maxf(dur, 0.1)

	_kill_tween()
	vignette_started.emit()

	_tween = create_tween()
	_tween.tween_property(_rect, "modulate:a", intensity, dur * 0.5)
	if intensity > 0:
		_tween.tween_interval(dur * 0.3)
	_tween.tween_property(_rect, "modulate:a", 0.0, dur * 0.5)
	_tween.tween_callback(_on_finished)


func _on_finished() -> void:
	_tween = null
	if _rect:
		_rect.modulate.a = 0.0
	vignette_finished.emit()


func _kill_tween() -> void:
	if _tween and is_instance_valid(_tween):
		_tween.kill()
	_tween = null


func is_active() -> bool:
	return _tween != null
