## Node que gerencia autoridade de rede (server/client).
## Generos: multiplayer.
## Tags: multiplayer, authority.
## Extends: Node.
## Sinais: authority_changed().
## Dependencias: nenhuma.
## @behavior: authority
@tool class_name Authority extends Node
@export var authority_type: String = "server"
signal authority_changed(new_peer_id: int)
var _current_authority: int = 1
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	if multiplayer and multiplayer.multiplayer_peer: _current_authority=multiplayer.get_unique_id()
	_initialized=true
func get_authority() -> int: return _current_authority
func is_server() -> bool: return _current_authority==1
func transfer(to_peer: int) -> void:
	_current_authority=to_peer; authority_changed.emit(to_peer)
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not multiplayer or not multiplayer.multiplayer_peer: w.append("Multiplayer peer não configurado.")
	return w
