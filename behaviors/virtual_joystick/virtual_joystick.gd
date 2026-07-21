## Behavior Virtual Joystick para Godot 4.
## Generos: mobile.
## Tags: touch.
## Extends: Node.
## Sinais: joystick_moved().
## Dependencias: nenhuma.
## @behavior: virtual_joystick
@tool class_name VirtualJoystick extends Control
@export var radius: float = 80.0: set(v)=radius=clampf(v,30.0,300.0)
@export var dead_zone: float = 10.0: set(v)=dead_zone=clampf(v,0.0,50.0)
signal joystick_moved(direction: Vector2); signal joystick_released()
var _pressed: bool = false; var _center: Vector2
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _center=size/2.0; _initialized=true
func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		var te:=event as InputEventScreenTouch; _pressed=te.pressed
		if not _pressed: joystick_released.emit()
	elif event is InputEventScreenDrag and _pressed:
		var de:=event as InputEventScreenDrag
		var dir:=(de.position-_center)/radius
		if dir.length()<dead_zone/radius: return
		dir=dir.limit_length(1.0); joystick_moved.emit(dir)
func _draw() -> void: draw_circle(_center,radius,Color(1,1,1,0.1)); if _pressed: draw_circle(_center,dead_zone,Color(1,1,1,0.2))
func _get_configuration_warnings() -> PackedStringArray: return []
