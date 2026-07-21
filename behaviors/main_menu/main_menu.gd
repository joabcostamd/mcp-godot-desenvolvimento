## MainMenu — Menu Principal | Godot 4.7 Style Guide compliant.
##
## CanvasLayer com botões Play, Settings e Quit.
## Configurável: cenas de destino, visibilidade dos botões.
##
## @behavior: main_menu
## @genres: generic
## @tutorial: behaviors/main_menu/README.md

@tool
class_name MainMenu
extends CanvasLayer

@export var play_scene: String = "res://scenes/game.tscn"
@export var settings_scene: String = "res://scenes/settings.tscn"
@export var show_quit: bool = true
@export var show_settings: bool = true

signal play_pressed()
signal settings_pressed()
signal quit_pressed()

var _container: VBoxContainer = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_setup_menu()
	_initialized = true


func _setup_menu() -> void:
	# Container central
	_container = VBoxContainer.new()
	_container.name = "MenuContainer"
	_container.set_anchors_preset(Control.PRESET_CENTER)
	_container.add_theme_constant_override("separation", 12)
	add_child(_container)

	# Título
	var title := Label.new()
	title.name = "TitleLabel"
	title.text = "Game Title"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 48)
	_container.add_child(title)

	# Botão Play
	_add_button("Play", _on_play)

	# Botão Settings
	if show_settings:
		_add_button("Settings", _on_settings)

	# Botão Quit
	if show_quit:
		_add_button("Quit", _on_quit)


func _add_button(text: String, callback: Callable) -> void:
	var btn := Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(200, 50)
	btn.pressed.connect(callback)
	_container.add_child(btn)


func _on_play() -> void:
	play_pressed.emit()
	if play_scene and ResourceLoader.exists(play_scene):
		_transition_to(play_scene)


func _on_settings() -> void:
	settings_pressed.emit()
	if settings_scene and ResourceLoader.exists(settings_scene):
		_transition_to(settings_scene)


func _on_quit() -> void:
	quit_pressed.emit()
	get_tree().quit()


func _transition_to(scene: String) -> void:
	var st := SceneTransition.new()
	st.fade_color = Color.BLACK
	st.default_duration = 0.5
	add_child(st)
	st.transition_to(scene)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
