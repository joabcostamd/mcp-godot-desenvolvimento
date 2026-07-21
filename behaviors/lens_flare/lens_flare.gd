@tool class_name LensFlare extends Node2D
@export var flare_intensity: float = 1.0: set(v)=flare_intensity=clampf(v,0.0,3.0)
@export var sun_position: Vector2 = Vector2(0.5,0.2)
@export var flare_color: Color = Color(1.0,0.9,0.7,0.5): set(v)=flare_color=v
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func _process(_delta: float) -> void:
	queue_redraw()
func _draw() -> void:
	if flare_intensity<=0: return
	var vp:=get_viewport(); if not vp: return
	var size:=vp.get_visible_rect().size
	var sun_screen:=sun_position*size
	var center:=size/2.0
	var dir_to_sun:=sun_screen-center
	var steps:=6
	for i in range(1,steps+1):
		var t:=float(i)/float(steps)
		var pos:=center-dir_to_sun*t*0.5
		var alpha:=flare_intensity*(1.0-t)*0.3
		var radius:=8.0*(1.0-t)*flare_intensity
		draw_circle(pos,radius,Color(flare_color.r,flare_color.g,flare_color.b,alpha))
func _get_configuration_warnings() -> PackedStringArray:
	return []
