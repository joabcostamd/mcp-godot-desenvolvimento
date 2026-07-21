## Node que encapsula chamadas RPC multiplayer.
## Generos: multiplayer.
## Tags: multiplayer, rpc.
## Extends: Node.
## Sinais: rpc_sent(), rpc_received().
## Dependencias: nenhuma.
## @behavior: rpc_bridge
@tool class_name RpcBridge extends Node
@export var reliable: bool = true
@export var channel: int = 0: set(v)=channel=clampi(v,0,15)
signal rpc_sent(method: String)
signal rpc_received(method: String)
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return; _initialized=true
func send_rpc(method: String, args: Array = []) -> void:
	if not multiplayer or not multiplayer.multiplayer_peer: return
	rpc_sent.emit(method)
	if has_method(method): callv(method,args)
func broadcast_rpc(method: String, args: Array = []) -> void:
	send_rpc(method,args)
func receive_rpc(method: String) -> void: rpc_received.emit(method)
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not multiplayer or not multiplayer.multiplayer_peer: w.append("Multiplayer peer não configurado.")
	return w
