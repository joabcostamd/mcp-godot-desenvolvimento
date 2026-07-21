## SceneTransition — Transição de Cena | Godot 4.7 Style Guide compliant.
##
## CanvasLayer + ColorRect fullscreen para fade-out/in entre cenas.
## transition_to(scene_path, duration) — fade-out → change_scene → fade-in.
##
## @behavior: scene_transition
## @genres: generic
## @tutorial: behaviors/scene_transition/README.md

@tool
class_name SceneTransition
extends CanvasLayer

@export var fade_color: Color = Color.BLACK
@export var default_duration: float = 0.5: set(v): default_duration = clampf(v, 0.1, 5)

signal transition_started()
signal transition_finished()

var _rect: ColorRect = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_setup_rect()
	_initialized = true


func _setup_rect() -> void:
	_rect = ColorRect.new()
	_rect.name = "TransitionRect"
	_rect.color = fade_color
	_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_rect.modulate.a = 0.0
	add_child(_rect)


## Executa transição para a cena alvo.
## duration < 0 usa default_duration.
func transition_to(scene_path: String, duration: float = -1.0) -> void:
	if not _rect:
		_setup_rect()

	var dur := default_duration if duration < 0 else duration
	dur = maxf(dur, 0.1)
	var half := dur * 0.5

	transition_started.emit()

	# Fade-out (cobre a tela)
	var tween := create_tween()
	tween.tween_property(_rect, "modulate:a", 1.0, half)
	tween.tween_callback(_change_scene.bind(scene_path, half))


func _change_scene(scene_path: String, fade_in_dur: float) -> void:
	# Troca a cena (assíncrono)
	get_tree().change_scene_to_file(scene_path)

	# Aguarda a cena carregar e faz fade-in
	await get_tree().process_frame
	await get_tree().process_frame

	var tween := create_tween()
	tween.tween_property(_rect, "modulate:a", 0.0, fade_in_dur)
	tween.tween_callback(_on_done)


func _on_done() -> void:
	transition_finished.emit()


func is_active() -> bool:
	return _rect != null and _rect.modulate.a > 0.0
