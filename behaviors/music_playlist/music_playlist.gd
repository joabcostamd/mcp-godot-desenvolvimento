## MusicPlaylist — Playlist de Música | Godot 4.7 Style Guide compliant.
##
## Gerencia array de AudioStream com shuffle, crossfade e navegação.
## play()/next()/prev(). Usa bus Music.
##
## @behavior: music_playlist
## @genres: generic
## @tutorial: behaviors/music_playlist/README.md

@tool
class_name MusicPlaylist
extends Node

@export var tracks: Array[AudioStream] = []
@export var shuffle: bool = false: set = _set_shuffle
@export var crossfade_duration: float = 0.0: set(v): crossfade_duration = clampf(v, 0, 5)
@export var volume_db: float = 0.0: set(v): volume_db = clampf(v, -80, 24)
@export var auto_play: bool = false

signal track_changed(track_index: int)
signal playlist_finished()

var _current_index: int = -1
var _player_current: AudioStreamPlayer = null
var _player_next: AudioStreamPlayer = null
var _shuffled_indices: Array[int] = []
var _rng := RandomNumberGenerator.new()
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_rng.randomize()
	_build_indices()
	_initialized = true
	if auto_play and tracks.size() > 0:
		play()


func _set_shuffle(v: bool) -> void:
	shuffle = v
	_build_indices()


func _build_indices() -> void:
	_shuffled_indices.clear()
	for i in tracks.size():
		_shuffled_indices.append(i)
	if shuffle:
		for i in range(_shuffled_indices.size() - 1, 0, -1):
			var j := _rng.randi_range(0, i)
			var tmp := _shuffled_indices[i]
			_shuffled_indices[i] = _shuffled_indices[j]
			_shuffled_indices[j] = tmp


## Inicia a playlist a partir da primeira faixa.
func play() -> void:
	if tracks.is_empty():
		return
	_current_index = -1
	_play_track(0)


## Próxima faixa.
func next() -> void:
	if tracks.is_empty():
		return
	var nxt := _current_index + 1
	if nxt >= _shuffled_indices.size():
		playlist_finished.emit()
		return
	_play_track(nxt)


## Faixa anterior.
func prev() -> void:
	if tracks.is_empty() or _current_index <= 0:
		return
	_play_track(_current_index - 1)


func _play_track(list_index: int) -> void:
	_current_index = list_index
	var track_idx := _shuffled_indices[list_index]
	var stream := tracks[track_idx]

	# Crossfade: fade-out atual, fade-in nova
	if crossfade_duration > 0 and _player_current and is_instance_valid(_player_current):
		_player_next = _create_player(stream)
		_player_next.volume_db = -80.0
		_player_next.play()
		var tw := create_tween()
		tw.set_parallel(true)
		tw.tween_property(_player_current, "volume_db", -80.0, crossfade_duration)
		tw.tween_property(_player_next, "volume_db", volume_db, crossfade_duration)
		tw.tween_callback(_on_crossfade_done)
	else:
		_stop_current()
		_player_current = _create_player(stream)
		_player_current.play()

	track_changed.emit(list_index)


func _create_player(stream: AudioStream) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.stream = stream
	p.bus = "Music"
	p.volume_db = volume_db
	p.finished.connect(_on_track_finished)
	add_child(p)
	return p


func _stop_current() -> void:
	if _player_current and is_instance_valid(_player_current):
		_player_current.stop()
		_player_current.queue_free()
	_player_current = null


func _on_track_finished() -> void:
	next()


func _on_crossfade_done() -> void:
	if _player_current and is_instance_valid(_player_current):
		_player_current.queue_free()
	_player_current = _player_next
	_player_next = null


## Para a reprodução.
func stop() -> void:
	_stop_current()
	if _player_next and is_instance_valid(_player_next):
		_player_next.queue_free()
	_player_next = null
	_current_index = -1


func is_playing() -> bool:
	return _player_current != null and is_instance_valid(_player_current) and _player_current.playing


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
