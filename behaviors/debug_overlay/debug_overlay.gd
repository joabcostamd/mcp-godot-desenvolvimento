@tool class_name DebugOverlay extends Control
@export var show_fps: bool = true
@export var show_memory: bool = true
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func _process(_delta: float) -> void: queue_redraw()
func _draw() -> void:
	var y:=10.0
	if show_fps: draw_string(ThemeDB.fallback_font,Vector2(10,y),"FPS: "+str(Engine.get_frames_per_second())); y+=20
	if show_memory: draw_string(ThemeDB.fallback_font,Vector2(10,y),"Mem: "+str(snapped(OS.get_static_memory_usage()/1048576.0,0.1))+" MB")
func _get_configuration_warnings() -> PackedStringArray: return []
