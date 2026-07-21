## Node que detecta gestos touch: swipe, pinch, long press, double tap.
## Generos: mobile.
## Tags: touch.
## Extends: Node.
## Sinais: swiped(), pinched(), long_pressed(), double_tapped().
## Dependencias: nenhuma.
## @behavior: touch_gestures
@tool class_name TouchGestures extends Node
@export var swipe_threshold: float = 50.0: set(v)=swipe_threshold=clampf(v,10.0,200.0)
signal swiped(direction: Vector2); signal pinched(scale: float); signal long_pressed(position: Vector2); signal double_tapped(position: Vector2)
var _touch_start: Vector2; var _last_tap_time: float = 0.0; var _last_tap_pos: Vector2; var _long_press_emitted: bool = false
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func _process(_delta: float) -> void:
	if not _long_press_emitted and Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
		var now:=Time.get_ticks_msec()/1000.0
		if now-_last_tap_time>0.5: _long_press_emitted=true; long_pressed.emit(_touch_start)
func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		var te:=event as InputEventScreenTouch
		if te.pressed:
			_touch_start=te.position; _long_press_emitted=false
			var now:=Time.get_ticks_msec()/1000.0
			if now-_last_tap_time<0.3 and te.position.distance_to(_last_tap_pos)<50.0: double_tapped.emit(te.position)
			_last_tap_time=now; _last_tap_pos=te.position
		else:
			var delta:=te.position-_touch_start
			if delta.length()>swipe_threshold: swiped.emit(delta.normalized())
	elif event is InputEventScreenDrag:
		var de:=event as InputEventScreenDrag
		if de.get_relative().length()>1.0 and de.index==1: pinched.emit(de.get_relative().length()/100.0)
func _get_configuration_warnings() -> PackedStringArray: return []
