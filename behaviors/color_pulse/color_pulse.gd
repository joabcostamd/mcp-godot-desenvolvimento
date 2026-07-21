## ColorPulse — Pulsação de Cor | Godot 4.7 Style Guide compliant.
##
## Aplica pulsação rítmica no modulate do nó pai via _process + sin().
## start()/stop() controlam. auto_start inicia automaticamente.
## Restaura modulate original ao parar.
##
## @behavior: color_pulse
## @genres: generic
## @tutorial: behaviors/color_pulse/README.md

@tool
class_name ColorPulse
extends Node

@export var pulse_color: Color = Color.RED
@export var frequency: float = 2.0: set(v): frequency = clampf(v, 0.1, 30)
@export var amplitude: float = 0.5: set(v): amplitude = clampf(v, 0, 1)
@export var auto_start: bool = true

signal pulsing(is_active: bool)

var _active: bool = false
var _original_modulate: Color = Color.WHITE
var _start_time: int = 0
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	var parent := get_parent()
	if parent and parent is CanvasItem:
		_original_modulate = (parent as CanvasItem).modulate
	_initialized = true
	if auto_start:
		start()


func _process(_delta: float) -> void:
	if not _active:
		return

	var parent := get_parent()
	if not parent or not parent is CanvasItem:
		return

	var elapsed := (Time.get_ticks_msec() - _start_time) / 1000.0
	var t := sin(elapsed * frequency * TAU)  # -1..1
	t = (t + 1.0) * 0.5  # 0..1

	var modulated := _original_modulate.lerp(pulse_color, t * amplitude)
	(parent as CanvasItem).modulate = modulated


## Inicia a pulsação.
func start() -> void:
	_active = true
	_start_time = Time.get_ticks_msec()
	pulsing.emit(true)


## Para a pulsação e restaura modulate original.
func stop() -> void:
	_active = false
	var parent := get_parent()
	if parent and parent is CanvasItem:
		(parent as CanvasItem).modulate = _original_modulate
	pulsing.emit(false)


func is_pulsing() -> bool:
	return _active
