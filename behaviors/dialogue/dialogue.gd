## Dialogue — Sistema de Diálogo | Godot 4.7 Style Guide compliant.
##
## CanvasLayer + RichTextLabel para exibir linhas de diálogo.
## next() avança; auto_advance com Timer; advance_input escuta ação.
##
## @behavior: dialogue
## @genres: rpg, platformer, generic
## @tutorial: behaviors/dialogue/README.md

@tool
class_name Dialogue
extends CanvasLayer

@export var lines: Array = []
@export var auto_advance: bool = false
@export var auto_delay: float = 3.0: set(v): auto_delay = clampf(v, 0.5, 30)
@export var advance_input: String = "ui_accept"

signal dialogue_started()
signal line_displayed(index: int)
signal dialogue_finished()

var _current_index: int = -1
var _active: bool = false
var _auto_timer: Timer = null
var _label: RichTextLabel = null
var _speaker_label: Label = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_setup_ui()
	_initialized = true


func _setup_ui() -> void:
	var panel := Panel.new()
	panel.name = "DialoguePanel"
	panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	panel.position = Vector2(0, -150)
	panel.size = Vector2(0, 120)
	add_child(panel)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 4)
	panel.add_child(vbox)

	_speaker_label = Label.new()
	_speaker_label.name = "SpeakerLabel"
	_speaker_label.add_theme_font_size_override("font_size", 18)
	_speaker_label.text = ""
	vbox.add_child(_speaker_label)

	_label = RichTextLabel.new()
	_label.name = "DialogueLabel"
	_label.bbcode_enabled = true
	_label.fit_content = true
	_label.scroll_following = true
	vbox.add_child(_label)


func _input(event: InputEvent) -> void:
	if not _active: return
	if advance_input and event.is_action_pressed(advance_input):
		next()
	elif not advance_input and event.is_pressed():
		next()


## Inicia o diálogo com as linhas configuradas.
func start(lines_override: Array = []) -> void:
	if lines_override.size() > 0:
		lines = lines_override
	if lines.is_empty(): return

	_current_index = -1
	_active = true
	dialogue_started.emit()
	_show_line(0)


func _show_line(idx: int) -> void:
	_current_index = idx
	var data: Dictionary = lines[idx]
	var text: String = data.get("text", "")
	var speaker: String = data.get("speaker", "")

	if _speaker_label:
		_speaker_label.text = speaker
	if _label:
		_label.text = text

	line_displayed.emit(idx)

	if auto_advance:
		_start_auto_timer()


func next() -> void:
	_kill_timer()
	var nxt := _current_index + 1
	if nxt >= lines.size():
		_finish()
		return
	_show_line(nxt)


func _start_auto_timer() -> void:
	_kill_timer()
	_auto_timer = Timer.new()
	_auto_timer.one_shot = true
	_auto_timer.wait_time = auto_delay
	_auto_timer.timeout.connect(next)
	add_child(_auto_timer)
	_auto_timer.start()


func _kill_timer() -> void:
	if _auto_timer:
		_auto_timer.queue_free()
		_auto_timer = null


func _finish() -> void:
	_active = false
	_kill_timer()
	dialogue_finished.emit()


func skip() -> void:
	_finish()


func is_active() -> bool:
	return _active
