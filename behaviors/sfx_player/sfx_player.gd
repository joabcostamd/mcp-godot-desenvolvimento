## SfxPlayer — Player de SFX | Godot 4.7 Style Guide compliant.
##
## AudioStreamPlayer wrapper para one-shot com auto-limpeza.
## play() toca o stream padrão; play_stream() sobrescreve.
##
## @behavior: sfx_player
## @genres: generic
## @tutorial: behaviors/sfx_player/README.md

@tool
class_name SfxPlayer
extends Node

@export var audio_stream: AudioStream = null
@export var volume_db: float = 0.0: set(v): volume_db = clampf(v, -80, 24)
@export var pitch_scale: float = 1.0: set(v): pitch_scale = clampf(v, 0.1, 4)
@export var bus: String = "SFX"
@export var auto_play: bool = false

signal played()
signal finished()

var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_initialized = true
	if auto_play and audio_stream:
		play()


## Toca o audio_stream padrão. Retorna o player ou null.
func play() -> AudioStreamPlayer:
	if not audio_stream:
		return null
	return _create_and_play(audio_stream)


## Toca um stream específico (sobrescreve o padrão para esta execução).
func play_stream(stream: AudioStream) -> AudioStreamPlayer:
	if not stream:
		return null
	return _create_and_play(stream)


func _create_and_play(stream: AudioStream) -> AudioStreamPlayer:
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.volume_db = volume_db
	player.pitch_scale = pitch_scale
	player.bus = bus
	player.finished.connect(_on_finished.bind(player))
	add_child(player)
	player.play()
	played.emit()
	return player


func _on_finished(p: AudioStreamPlayer) -> void:
	finished.emit()
	if is_instance_valid(p):
		p.queue_free()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
