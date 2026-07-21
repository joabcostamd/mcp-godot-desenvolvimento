## Behavior l_system para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: l_system
@tool class_name LSystem extends Node2D
@export var axiom: String = "F": set(v)=axiom=v
@export var rules: Dictionary = {"F":"F[+F]F[-F]F"}: set(v)=rules=v
@export var iterations: int = 3: set(v)=iterations=clampi(v,1,10)
@export var angle: float = 25.0: set(v)=angle=clampf(v,5.0,180.0)
@export var length: float = 10.0: set(v)=length=clampf(v,1.0,200.0)
signal generation_finished()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func generate() -> String:
	var s:=axiom
	for _i in iterations:
		var ns:=""
		for c in s:
			var r: String=rules.get(c,"")
			ns+=r if not r.is_empty() else c
		s=ns
	generation_finished.emit(); return s
func _draw() -> void:
	var s:=generate(); var pos:=Vector2.ZERO; var dir:=Vector2.UP; var stack:=[]; var seg:=length/pow(3,iterations)
	for c in s:
		match c: "F": draw_line(pos,pos+dir*seg,Color.GREEN); pos+=dir*seg; "+": dir=dir.rotated(deg_to_rad(angle)); "-": dir=dir.rotated(deg_to_rad(-angle)); "[": stack.append([pos,dir]); "]": if not stack.is_empty(): var st=stack.pop_back(); pos=st[0]; dir=st[1]
func _get_configuration_warnings() -> PackedStringArray: return []
