@tool class_name Lobby extends Node
@export var max_players: int = 4: set(v)=max_players=clampi(v,2,64)
@export var game_mode: String = "default"
signal player_joined(peer_id: int)
signal player_left(peer_id: int)
signal game_started()
var _players: Array[int] = []
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
	if multiplayer and multiplayer.multiplayer_peer:
		multiplayer.peer_connected.connect(_on_peer_connected)
		multiplayer.peer_disconnected.connect(_on_peer_disconnected)
func _on_peer_connected(id: int) -> void:
	if _players.size()>=max_players: return
	_players.append(id); player_joined.emit(id)
	if _players.size()>=max_players: game_started.emit()
func _on_peer_disconnected(id: int) -> void:
	var idx:=_players.find(id)
	if idx>=0: _players.remove_at(idx); player_left.emit(id)
func get_players() -> Array[int]: return _players.duplicate()
func get_player_count() -> int: return _players.size()
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not multiplayer or not multiplayer.multiplayer_peer: w.append("Multiplayer peer não configurado.")
	return w
