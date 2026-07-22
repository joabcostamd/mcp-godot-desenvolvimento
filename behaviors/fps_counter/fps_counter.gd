## FpsCounter — Contador de FPS | Godot 4.7.
@tool
class_name FpsCounter
extends Control

@export var update_interval: float = 0.5: set(v): update_interval=clampf(v,0.1,5)
@export var show_min_max: bool = true

var _label: Label
var _timer: float=0; var _frames:int=0; var _fps:float=0
var _min_fps:float=9999; var _max_fps:float=0
var _initialized:bool=false

func _ready() -> void:
	if _initialized: return
	_label=Label.new(); _label.name="FPSLabel"; _label.add_theme_font_size_override("font_size",14)
	_label.position=Vector2(8,8); add_child(_label)
	set_anchors_preset(Control.PRESET_TOP_LEFT); _initialized=true

func _process(delta: float) -> void:
	_timer+=delta; _frames+=1
	if _timer>=update_interval:
		_fps=_frames/_timer
		if _fps<_min_fps: _min_fps=_fps
		if _fps>_max_fps: _max_fps=_fps
		_timer=0; _frames=0
	var text:=str(int(_fps))+" FPS"
	if show_min_max: text+=" | min:"+str(int(_min_fps))+" max:"+str(int(_max_fps))
	_label.text=text


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
