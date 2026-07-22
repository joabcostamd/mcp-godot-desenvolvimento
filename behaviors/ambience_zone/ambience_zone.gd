## AmbienceZone — Zona de Som Ambiente | Godot 4.7 Style Guide compliant.
##
## Area2D + AudioStreamPlayer2D filho para som ambiente com atenuação.
## Toca ao detectar body; para ao sair. auto_play ignora detecção.
##
## @behavior: ambience_zone
## @genres: generic
## @tutorial: behaviors/ambience_zone/README.md

@tool
class_name AmbienceZone
extends Area2D

@export var audio_stream: AudioStream = null
@export var volume_db: float = 0.0: set(v): volume_db = clampf(v, -80, 24)
@export var max_distance: float = 500.0: set(v): max_distance = clampf(v, 10, 5000)
@export var attenuation: float = 0.5: set(v): attenuation = clampf(v, 0, 1)
@export var auto_play: bool = false

signal entered_zone()
signal exited_zone()

var _player: AudioStreamPlayer2D = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	_setup_player()
	_setup_collision()
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	_initialized = true
	if auto_play:
		_play()


func _setup_player() -> void:
	_player = AudioStreamPlayer2D.new()
	_player.name = "AmbiencePlayer"
	_player.stream = audio_stream
	_player.volume_db = volume_db
	_player.max_distance = max_distance
	_player.attenuation = attenuation
	_player.bus = "SFX"
	add_child(_player)


func _setup_collision() -> void:
	var shape := CollisionShape2D.new()
	shape.name = "AmbienceShape"
	var rect := RectangleShape2D.new()
	rect.size = Vector2(200, 200)
	shape.shape = rect
	add_child(shape)


func _on_body_entered(_body: Node2D) -> void:
	_play()
	entered_zone.emit()


func _on_body_exited(_body: Node2D) -> void:
	if not auto_play:
		_stop()
	exited_zone.emit()


func _play() -> void:
	if _player and audio_stream:
		_player.play()


func _stop() -> void:
	if _player:
		_player.stop()


func is_playing() -> bool:
	return _player != null and _player.playing


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("Consider setting collision_mask to detect specific layers.")
	return w
