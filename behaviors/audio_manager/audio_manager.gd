## AudioManager — Gerenciador de Áudio | Godot 4.7 Style Guide compliant.
##
## Controla volume dos buses Master, Music, SFX via AudioServer.
## play_sfx(stream) e play_music(stream) criam players temporários.
##
## @behavior: audio_manager
## @genres: generic
## @tutorial: behaviors/audio_manager/README.md

@tool
class_name AudioManager
extends Node

@export var master_volume_db: float = 0.0: set(v): _set_bus_volume("Master", v)
@export var music_volume_db: float = 0.0: set(v): _set_bus_volume("Music", v)
@export var sfx_volume_db: float = 0.0: set(v): _set_bus_volume("SFX", v)

var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	# Aplica volumes iniciais
	_set_bus_volume("Master", master_volume_db)
	_set_bus_volume("Music", music_volume_db)
	_set_bus_volume("SFX", sfx_volume_db)
	_initialized = true


## Toca um som SFX (one-shot). Retorna o player para controle.
func play_sfx(stream: AudioStream, volume_db := 0.0, pitch := 1.0) -> AudioStreamPlayer:
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.bus = "SFX"
	player.volume_db = volume_db
	player.pitch_scale = pitch
	player.finished.connect(player.queue_free)
	add_child(player)
	player.play()
	return player


## Toca música (em loop). Retorna o player.
func play_music(stream: AudioStream, volume_db := 0.0) -> AudioStreamPlayer:
	# Para música anterior
	_stop_bus_players("Music")

	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.bus = "Music"
	player.volume_db = volume_db
	add_child(player)
	player.play()
	return player


## Define volume de um bus pelo nome.
func set_bus_volume(bus_name: String, volume_db: float) -> void:
	_set_bus_volume(bus_name, volume_db)


func _set_bus_volume(bus_name: String, volume_db: float) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx >= 0:
		var clamped := clampf(volume_db, -80, 24)
		AudioServer.set_bus_volume_db(idx, clamped)


## Retorna o volume atual de um bus.
func get_bus_volume(bus_name: String) -> float:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx >= 0:
		return AudioServer.get_bus_volume_db(idx)
	return 0.0


func _stop_bus_players(bus_name: String) -> void:
	for child in get_children():
		if child is AudioStreamPlayer:
			var p := child as AudioStreamPlayer
			if p.bus == bus_name and p.playing:
				p.stop()
				p.queue_free()
