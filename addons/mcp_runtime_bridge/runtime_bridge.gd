extends Node
## Autoload: MCPRuntimeBridge
## Servidor TCP local, so ativo em debug build, que expoe estado do jogo
## rodando para o MCP Python via protocolo JSON-por-linha.

const PORT := 8790
const HOST := "127.0.0.1"

var _server: TCPServer = null
var _peer: StreamPeerTCP = null
var _custom_commands: Dictionary = {}
# Fila para comandos pendentes que precisam de espera (ex: wait_frames)
var _pending_commands: Array[Dictionary] = []

func _ready() -> void:
	if not OS.is_debug_build():
		return
	_server = TCPServer.new()
	var err := _server.listen(PORT, HOST)
	if err != OK:
		push_warning("MCPRuntimeBridge: falha ao abrir porta %d (err %d)" % [PORT, err])
		return
	print("MCPRuntimeBridge: escutando em %s:%d" % [HOST, PORT])


func register_command(cmd_name: String, callable: Callable) -> void:
	_custom_commands[cmd_name] = callable


func _process(_delta: float) -> void:
	if _server == null:
		return

	if _server.is_connection_available():
		_peer = _server.take_connection()

	if _peer == null:
		return

	_peer.poll()
	var status := _peer.get_status()
	if status != StreamPeerTCP.STATUS_CONNECTED:
		_peer = null
		return

	var available := _peer.get_available_bytes()
	if available <= 0:
		return

	var raw := _peer.get_utf8_string(available)
	if raw == "":
		return

	for line in raw.split("\n", false):
		var trimmed := line.strip_edges()
		if trimmed == "":
			continue
		var json := JSON.new()
		if json.parse(trimmed) != OK:
			_reply({"ok": false, "error": "JSON invalido: %s" % trimmed})
			continue
		var msg: Dictionary = json.data
		var cmd: String = msg.get("cmd", "")
		match cmd:
			"screenshot":
				_reply(_cmd_screenshot())
			"runtime_info":
				_reply(_cmd_runtime_info())
			"list_commands":
				_reply({"ok": true, "commands": _custom_commands.keys()})
			"custom":
				_reply(_cmd_custom(msg.get("name", ""), msg.get("args", {})))
			"input_event":
				_reply(_cmd_input_event(msg.get("event", {})))
			"wait_frames":
				_reply({"ok": true, "note": "wait_frames recebido — frames processados naturalmente"})
			_:
				_reply({"ok": false, "error": "comando desconhecido: %s" % cmd})


func _cmd_screenshot() -> Dictionary:
	var viewport := get_viewport()
	if viewport == null:
		return {"ok": false, "error": "viewport indisponivel"}
	var img := viewport.get_texture().get_image()
	if img == null:
		return {"ok": false, "error": "imagem indisponivel"}
	var png_bytes := img.save_png_to_buffer()
	return {
		"ok": true,
		"width": img.get_width(),
		"height": img.get_height(),
		"image_base64": Marshalls.raw_to_base64(png_bytes),
	}


func _cmd_runtime_info() -> Dictionary:
	var draw_calls := RenderingServer.get_rendering_info(
		RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME
	)
	return {
		"ok": true,
		"fps": Engine.get_frames_per_second(),
		"draw_calls": draw_calls,
		"static_memory_mb": OS.get_static_memory_usage() / 1048576.0,
		"physics_process_time_ms": Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0,
	}


func _cmd_custom(cmd_name: String, args: Dictionary) -> Dictionary:
	if not _custom_commands.has(cmd_name):
		return {"ok": false, "error": "comando customizado nao registrado: %s" % cmd_name}
	var result = _custom_commands[cmd_name].call(args)
	return {"ok": true, "result": result}


func _cmd_input_event(event_data: Dictionary) -> Dictionary:
	var event_type: String = event_data.get("type", "")
	match event_type:
		"mouse_click":
			var ev := InputEventMouseButton.new()
			ev.button_index = MOUSE_BUTTON_LEFT
			ev.pressed = true
			ev.position = Vector2(event_data.get("x", 0), event_data.get("y", 0))
			Input.parse_input_event(ev)
			ev = ev.duplicate()
			ev.pressed = false
			Input.parse_input_event(ev)
			return {"ok": true}
		"key":
			var ev := InputEventKey.new()
			ev.keycode = event_data.get("keycode", 0)
			ev.pressed = true
			Input.parse_input_event(ev)
			ev = ev.duplicate()
			ev.pressed = false
			Input.parse_input_event(ev)
			return {"ok": true}
		_:
			return {"ok": false, "error": "tipo de evento desconhecido: %s" % event_type}


func _reply(data: Dictionary) -> void:
	if _peer == null:
		return
	var out := JSON.stringify(data) + "\n"
	_peer.put_data(out.to_utf8_buffer())
