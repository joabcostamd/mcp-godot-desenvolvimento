## DebugPosition — Marcador de Debug | Godot 4.7.
@tool
class_name DebugPosition
extends Node2D

@export var color: Color = Color.MAGENTA: set(v): color=v; queue_redraw()
@export var size: float = 16.0: set(v): size=clampf(v,4,64); queue_redraw()
@export var show_label: bool = false: set(v): show_label=v; queue_redraw()

func _draw() -> void:
	draw_line(Vector2(-size,0),Vector2(size,0),color,2)
	draw_line(Vector2(0,-size),Vector2(0,size),color,2)
	draw_circle(Vector2.ZERO,size*0.3,Color(color,0.3))
	if show_label:
		var p:=get_parent(); var t:=""
		if p is Node2D: t=str((p as Node2D).global_position)
		draw_string(ThemeDB.fallback_font,Vector2(size+4,4),t,HORIZONTAL_ALIGNMENT_LEFT,-1,10,color)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
