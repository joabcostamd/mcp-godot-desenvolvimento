@tool class_name Subtitle extends Control
@export var subtitle_text: String = "": set(v)=subtitle_text=v; _update_label()
@export var duration: float = 3.0: set(v)=duration=clampf(v,0.5,30.0)
signal shown(); signal hidden()
var _label: Label; var _timer: Timer; var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	_label=Label.new(); _label.visible=false; add_child(_label)
	_timer=Timer.new(); _timer.one_shot=true; _timer.timeout.connect(_hide); add_child(_timer)
	_initialized=true
func show_subtitle(text: String="", dur: float=-1.0) -> void:
	if not text.is_empty(): subtitle_text=text
	if dur>0: duration=dur
	_label.visible=true; shown.emit(); _timer.start(duration)
func _hide() -> void: _label.visible=false; hidden.emit()
func _update_label() -> void: if _label: _label.text=subtitle_text
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if subtitle_text.is_empty(): w.append("subtitle_text vazio.")
	return w
