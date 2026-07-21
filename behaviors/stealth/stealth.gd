@tool class_name Stealth extends Node
@export var visibility: float = 0.5: set(v): visibility=clampf(v,0,1)
@export var noise_radius: float = 100.0: set(v): noise_radius=clampf(v,0,500)
@export var detection_decay: float = 0.5
signal detected(); signal alerted(); signal hidden()
var _detection: float = 0.0; var _detected: bool = false

func _physics_process(delta: float) -> void:
	_detection=maxf(0,_detection-detection_decay*delta)
	if _detection<=0 and _detected: _detected=false; hidden.emit()

func add_detection(amount: float) -> void:
	_detection=minf(1.0,_detection+amount)
	if _detection>=1.0 and not _detected: _detected=true; detected.emit()
	elif _detection>=0.5 and not _detected: alerted.emit()

func make_noise() -> void: add_detection(0.3*(1.0-visibility))
func get_detection_level() -> float: return _detection
func is_detected() -> bool: return _detected
