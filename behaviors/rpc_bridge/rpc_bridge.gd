@tool class_name RPCBridge extends Node
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
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if not multiplayer or not multiplayer.multiplayer_peer: w.append("Multiplayer peer não configurado.")
	return w
