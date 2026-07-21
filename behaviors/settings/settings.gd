## Settings — Tela de Configurações | Godot 4.7 Style Guide compliant.
##
## CanvasLayer com sliders de volume, toggle fullscreen e seletor idioma.
## apply() persiste via SaveLoad; revert() descarta mudanças.
##
## @behavior: settings
## @genres: generic
## @tutorial: behaviors/settings/README.md

@tool
class_name Settings
extends CanvasLayer

@export var default_master_vol: float = 0.0
@export var default_music_vol: float = 0.0
@export var default_sfx_vol: float = 0.0
@export var show_fullscreen: bool = true
@export var show_language: bool = false

signal setting_changed(setting: String, value: Variant)

var _slider_master: HSlider = null
var _slider_music: HSlider = null
var _slider_sfx: HSlider = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_setup_ui()
	_load_saved()
	_initialized = true


func _setup_ui() -> void:
	var container := VBoxContainer.new()
	container.name = "SettingsContainer"
	container.set_anchors_preset(Control.PRESET_CENTER)
	container.add_theme_constant_override("separation", 8)
	add_child(container)

	var title := Label.new()
	title.text = "Settings"
	title.add_theme_font_size_override("font_size", 36)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	container.add_child(title)

	_slider_master = _add_slider(container, "Master", default_master_vol, _on_master_changed)
	_slider_music = _add_slider(container, "Music", default_music_vol, _on_music_changed)
	_slider_sfx = _add_slider(container, "SFX", default_sfx_vol, _on_sfx_changed)

	if show_fullscreen:
		var full_btn := CheckButton.new()
		full_btn.text = "Fullscreen"
		full_btn.button_pressed = _is_fullscreen()
		full_btn.toggled.connect(_on_fullscreen_toggled)
		container.add_child(full_btn)


func _add_slider(parent: Control, label: String, default_val: float, callback: Callable) -> HSlider:
	var hbox := HBoxContainer.new()
	var lbl := Label.new()
	lbl.text = label
	lbl.custom_minimum_size = Vector2(80, 0)
	hbox.add_child(lbl)

	var slider := HSlider.new()
	slider.min_value = -80.0
	slider.max_value = 24.0
	slider.step = 1.0
	slider.value = default_val
	slider.value_changed.connect(callback)
	slider.custom_minimum_size = Vector2(200, 0)
	hbox.add_child(slider)

	parent.add_child(hbox)
	return slider


func _load_saved() -> void:
	var sl := _find_save_load()
	if sl:
		var mv := sl.get_data("settings_master_vol", default_master_vol)
		var pv := sl.get_data("settings_music_vol", default_music_vol)
		var sv := sl.get_data("settings_sfx_vol", default_sfx_vol)
		_slider_master.value = mv
		_slider_music.value = pv
		_slider_sfx.value = sv
		_apply_volumes()


func _find_save_load() -> Node:
	var tree := get_tree()
	if tree:
		for node in tree.get_nodes_in_group("save_load"):
			if node.has_method("get_data"):
				return node
	return null


func _on_master_changed(v: float) -> void:
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Master"), v)
	setting_changed.emit("master_volume", v)


func _on_music_changed(v: float) -> void:
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Music"), v)
	setting_changed.emit("music_volume", v)


func _on_sfx_changed(v: float) -> void:
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("SFX"), v)
	setting_changed.emit("sfx_volume", v)


func _on_fullscreen_toggled(on: bool) -> void:
	if on:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	setting_changed.emit("fullscreen", on)


func _is_fullscreen() -> bool:
	return DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN


func _apply_volumes() -> void:
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Master"), _slider_master.value)
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Music"), _slider_music.value)
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("SFX"), _slider_sfx.value)


## Aplica e salva as configurações atuais.
func apply() -> void:
	var sl := _find_save_load()
	if sl and sl.has_method("set_data"):
		sl.set_data("settings_master_vol", _slider_master.value)
		sl.set_data("settings_music_vol", _slider_music.value)
		sl.set_data("settings_sfx_vol", _slider_sfx.value)
	_apply_volumes()
