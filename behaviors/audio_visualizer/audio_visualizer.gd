## Behavior audio_visualizer para Godot 4.
## Generos: generic.
## Extends: Node.
## Dependencias: nenhuma.
## @behavior: audio_visualizer
@tool class_name AudioVisualizer extends Node
@export var enabled: bool = true
signal sound_detected()
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func notify_sound() -> void: sound_detected.emit()
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not enabled: w.append("AudioVisualizer desabilitado.")
	return w
