## runtime_bridge_client.gd — MCP Runtime Bridge | Client wrapper para autoload.
##
## Conecta ao servidor TCP do MCPRuntimeBridge (porta 8790) e expoe
## uma API simples para comunicacao com o jogo rodando.
##
## Uso: adicione como autoload no project.godot:
##   [autoload]
##   RuntimeBridge="*res://addons/mcp_runtime_bridge/runtime_bridge_client.gd"
##
## @tutorial: https://docs.godotengine.org/en/stable/tutorials/scripting/singletons_autoload.html

extends Node

# ── Constantes ────────────────────────────────────────────────────────────────

const BRIDGE_HOST: String = "127.0.0.1"
const BRIDGE_PORT: int = 8790
const RECONNECT_INTERVAL: float = 3.0

# ── Estado ────────────────────────────────────────────────────────────────────

var _stream: StreamPeerTCP = null
var _connected: bool = false
var _reconnect_timer: float = 0.0
var _pending_requests: Array[Dictionary] = []

# ── Sinais ────────────────────────────────────────────────────────────────────

signal connected()
signal disconnected()
signal response_received(data: Dictionary)


# ── Ciclo de vida ─────────────────────────────────────────────────────────────

func _ready() -> void:
	_connect_to_bridge()


func _process(delta: float) -> void:
	if _stream:
		_process_stream()

	if not _connected:
		_reconnect_timer -= delta
		if _reconnect_timer <= 0.0:
			_connect_to_bridge()


func _exit_tree() -> void:
	if _stream:
		_stream = null


# ── API Publica ───────────────────────────────────────────────────────────────

func is_connected() -> bool:
	return _connected


func send_command(cmd: String, params: Dictionary = {}) -> void:
	"""Envia um comando JSON para o runtime bridge."""
	var msg: Dictionary = {"command": cmd, "params": params}
	_send_json(msg)


func save_current_scene(path: String = "") -> void:
	"""Salva a cena atual do jogo."""
	send_command("save_current_scene", {"path": path})


func play_audio(audio_name: String, volume: float = 1.0) -> void:
	"""Toca um audio pelo runtime bridge."""
	send_command("play_audio", {"name": audio_name, "volume": volume})


func set_volume(bus: String, volume_db: float) -> void:
	"""Ajusta volume de um bus de audio."""
	send_command("set_volume", {"bus": bus, "volume": volume_db})


func stop_audio() -> void:
	"""Para todo audio."""
	send_command("stop_audio", {})


func set_auto_dismiss(enabled: bool, action: String = "hide", interval_ms: int = 500) -> void:
	"""Configura auto-dismiss de dialogos modais."""
	send_command("set_auto_dismiss", {
		"enabled": enabled,
		"action": action,
		"interval_ms": interval_ms,
	})


func add_test_marker(marker: String) -> void:
	"""Adiciona marcador de teste."""
	send_command("add_test_marker", {"marker": marker})


# ── Internals ─────────────────────────────────────────────────────────────────

func _connect_to_bridge() -> void:
	if _stream:
		_stream = null
		_connected = false

	_stream = StreamPeerTCP.new()
	var err: int = _stream.connect_to_host(BRIDGE_HOST, BRIDGE_PORT)
	if err != OK:
		_reconnect_timer = RECONNECT_INTERVAL
		return

	_connected = true
	_reconnect_timer = RECONNECT_INTERVAL
	connected.emit()
	print_rich("[RuntimeBridge Client] Conectado ao jogo em %s:%d" % [BRIDGE_HOST, BRIDGE_PORT])


func _process_stream() -> void:
	if _stream.get_status() != StreamPeerTCP.STATUS_CONNECTED:
		_connected = false
		disconnected.emit()
		return

	var available: int = _stream.get_available_bytes()
	if available > 0:
		var data: PackedByteArray = _stream.get_partial_data(available)
		var text: String = data[1].get_string_from_utf8()
		_parse_response(text)


func _send_json(data: Dictionary) -> void:
	if not _stream or _stream.get_status() != StreamPeerTCP.STATUS_CONNECTED:
		_pending_requests.append(data)
		return

	var json: JSON = JSON.new()
	var text: String = json.stringify(data) + "\n"
	_stream.put_data(text.to_utf8_buffer())


func _parse_response(text: String) -> void:
	var json: JSON = JSON.new()
	var err: int = json.parse(text)
	if err != OK:
		return
	var data: Variant = json.get_data()
	if typeof(data) == TYPE_DICTIONARY:
		response_received.emit(data)
