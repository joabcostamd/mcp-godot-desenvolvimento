## Node2D que desenha uma seta colorida na direção configurada.
## Generos: generic.
## Tags: debug.
## Extends: Node2D.
## Dependencias: nenhuma.
## @behavior: debug_arrow
@tool
class_name DebugArrow
extends Node2D
@export var color: Color = Color.GREEN: set(v): color=v; queue_redraw()
@export var length: float = 64.0: set(v): length=clampf(v,8,256); queue_redraw()
@export var direction: Vector2 = Vector2(1,0): set(v): direction=v.normalized() if v.length()>0 else Vector2(1,0); queue_redraw()

func _draw() -> void:
	var tip:=direction*length; draw_line(Vector2.ZERO,tip,color,2)
	var perp:=Vector2(-direction.y,direction.x)*length*0.2
	draw_line(tip,tip-direction*length*0.25+perp,color,2)
	draw_line(tip,tip-direction*length*0.25-perp,color,2)


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
