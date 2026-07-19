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
# Feature: Auto-dismiss de diálogos modais durante testes
var _auto_dismiss_enabled := false
var _auto_dismiss_action := "hide"
var _auto_dismiss_interval_ms := 500
var _auto_dismiss_timer := 0.0

func _ready() -> void:
	if not OS.is_debug_build():
		return
	_server = TCPServer.new()
	var err := _server.listen(PORT, HOST)
	if err != OK:
		push_warning("MCPRuntimeBridge: falha ao abrir porta %d (err %d)" % [PORT, err])
		return
	register_command("save_current_scene", _cmd_save_current_scene)
	register_command("add_test_marker", _cmd_add_test_marker)
	register_command("replace_with_runtime_scene", _cmd_replace_with_runtime_scene)
	register_command("set_auto_dismiss", _cmd_set_auto_dismiss)
	register_command("play_audio", _cmd_play_audio)
	register_command("set_volume", _cmd_set_volume)
	register_command("stop_audio", _cmd_stop_audio)
	print("MCPRuntimeBridge: escutando em %s:%d" % [HOST, PORT])


func register_command(cmd_name: String, callable: Callable) -> void:
	_custom_commands[cmd_name] = callable


func _process(delta: float) -> void:
	# Auto-dismiss de diálogos modais (Feature C3)
	if _auto_dismiss_enabled:
		_auto_dismiss_timer += delta * 1000.0
		if _auto_dismiss_timer >= _auto_dismiss_interval_ms:
			_auto_dismiss_timer = 0.0
			_check_and_dismiss_dialogs()

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
	var result = null
	var had_error := false
	var error_msg := ""
	var fn: Callable = _custom_commands[cmd_name]
	if not fn.is_valid():
		return {"ok": false, "error": "callable invalido para comando: %s" % cmd_name}
	# Tenta executar o comando customizado com protecao contra crash
	var ret = fn.call(args)
	if ret is Dictionary:
		result = ret
	elif ret is String:
		result = ret
	else:
		result = str(ret)
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


func _cmd_save_current_scene(_args: Dictionary) -> Dictionary:
	var scene: Node = get_tree().current_scene
	if scene == null:
		return {"saved": false, "error": "nenhuma cena atual"}
	var scene_path: String = scene.scene_file_path
	if scene_path == "":
		return {"saved": false, "error": "cena atual nao tem arquivo associado (runtime)"}
	var packed := PackedScene.new()
	var err := packed.pack(scene)
	if err != OK:
		return {"saved": false, "error": "pack falhou: %d" % err, "path": scene_path}
	err = ResourceSaver.save(packed, scene_path)
	if err != OK:
		return {"saved": false, "error": "ResourceSaver.save falhou: %d" % err, "path": scene_path}
	print("MCPRuntimeBridge: cena salva em %s" % scene_path)
	return {"saved": true, "path": scene_path}


func _cmd_add_test_marker(_args: Dictionary) -> Dictionary:
	var scene: Node = get_tree().current_scene
	if scene == null:
		return {"ok": false, "error": "nenhuma cena atual"}
	var marker := Node.new()
	marker.name = "SavedMarker"
	scene.add_child(marker)
	marker.owner = scene
	print("MCPRuntimeBridge: marcador SavedMarker adicionado a cena")
	return {"ok": true, "marker_added": true}


func _cmd_replace_with_runtime_scene(_args: Dictionary) -> Dictionary:
	var old_scene: Node = get_tree().current_scene
	var new_root := Node.new()
	new_root.name = "RuntimeRoot"
	get_tree().root.add_child(new_root)
	get_tree().current_scene = new_root
	if old_scene != null:
		old_scene.queue_free()
	print("MCPRuntimeBridge: cena substituida por runtime (sem scene_file_path)")
	return {"ok": true, "runtime_scene": true}


func _reply(data: Dictionary) -> void:
	if _peer == null:
		return
	var out := JSON.stringify(data) + "\n"
	var err := _peer.put_data(out.to_utf8_buffer())
	if err != OK:
		push_warning("MCPRuntimeBridge: falha ao enviar resposta (err %d)" % err)
		_peer = null

# ── Auto-dismiss de diálogos modais (Feature C3) ──────────────

func _cmd_set_auto_dismiss(args: Dictionary) -> Dictionary:
	_auto_dismiss_enabled = args.get("enabled", false)
	_auto_dismiss_action = args.get("action", "hide")
	_auto_dismiss_interval_ms = args.get("check_interval_ms", 500)
	_auto_dismiss_timer = 0.0
	return {
		"ok": true,
		"enabled": _auto_dismiss_enabled,
		"action": _auto_dismiss_action,
	}


func _check_and_dismiss_dialogs() -> void:
	_dismiss_recursive(get_tree().root)


func _dismiss_recursive(node: Node) -> void:
	if node is AcceptDialog and node.visible:
		match _auto_dismiss_action:
			"confirm":
				if node.has_signal("confirmed"):
					node.emit_signal("confirmed")
				node.hide()
			"cancel":
				if node.has_signal("canceled"):
					node.emit_signal("canceled")
				node.hide()
			"hide", _:
				node.hide()
	for child in node.get_children():
		_dismiss_recursive(child)


# ── Comandos de Áudio (Fase 6 — Corrigido Auditoria C2/C3/C4/C5/M1) ──

func _cmd_play_audio(args: Dictionary) -> Dictionary:
	var node_path: String = args.get("node_path", "")
	var audio_file: String = args.get("audio_file", "")
	var bus: String = args.get("bus", "Master")
	var volume_db: float = args.get("volume_db", 0.0)
	var loop: bool = args.get("loop", false)

	var target: Node = null
	if node_path != "":
		target = get_node_or_null(node_path)
	if target == null:
		target = _find_audio_player(node_path)
	if target == null:
		target = AudioStreamPlayer.new()
		target.name = "MCP_AudioPlayer"
		get_tree().root.add_child(target)

	if not target is AudioStreamPlayer:
		return {"ok": false, "error": "No '%s' nao e um AudioStreamPlayer" % node_path}

	var player: AudioStreamPlayer = target as AudioStreamPlayer

	if audio_file != "":
		var stream: Resource = load(audio_file)
		# Godot 4.x: Fallback quando load() falha (caminho raw/absoluto)
		# - AudioStreamMP3.data: PackedByteArray (OK)
		# - AudioStreamWAV.data: PackedByteArray (OK)
		# - AudioStreamOggVorbis: usar load_from_buffer() static (packet_sequence é OggPacketSequence, não PackedByteArray)
		if stream == null:
			var fa := FileAccess.open(audio_file, FileAccess.READ)
			if fa:
				var buffer := fa.get_buffer(fa.get_length())
				fa.close()
				var ext := audio_file.get_extension().to_lower()
				if ext == "mp3":
					var s := AudioStreamMP3.new()
					if s:
						s.data = buffer
						stream = s
				elif ext == "wav":
					var s := AudioStreamWAV.new()
					if s:
						s.data = buffer
						stream = s
				else:
					# OGG/Vorbis e outros: load_from_buffer cria o OggPacketSequence internamente
					stream = AudioStreamOggVorbis.load_from_buffer(buffer)
		# Type-check: garantir que é AudioStream antes de atribuir
		if stream is AudioStream:
			player.stream = stream

	player.bus = bus
	player.volume_db = volume_db
	if loop and player.stream != null and player.stream is AudioStream:
		(player.stream as AudioStream).loop = true

	player.play()
	return {"ok": true, "node_path": player.get_path(), "action": "play", "bus": bus}


func _cmd_set_volume(args: Dictionary) -> Dictionary:
	var node_path: String = args.get("node_path", "")
	var bus_name: String = args.get("bus_name", "Master")
	var volume_db: float = args.get("volume_db", 0.0)

	if node_path != "":
		var player = get_node_or_null(node_path)
		if player is AudioStreamPlayer:
			player.volume_db = volume_db
			return {"ok": true, "target": "player", "node_path": node_path, "volume_db": volume_db}
		return {"ok": false, "error": "AudioStreamPlayer nao encontrado: %s" % node_path}

	var bus_idx := AudioServer.get_bus_index(bus_name)
	if bus_idx < 0:
		return {"ok": false, "error": "Bus nao encontrado: %s" % bus_name}
	AudioServer.set_bus_volume_db(bus_idx, volume_db)
	return {"ok": true, "target": "bus", "bus_name": bus_name, "volume_db": volume_db}


func _cmd_stop_audio(args: Dictionary) -> Dictionary:
	var node_path: String = args.get("node_path", "")
	var stopped := 0

	if node_path != "":
		var player = get_node_or_null(node_path)
		if player is AudioStreamPlayer:
			player.stop()
			stopped = 1
	else:
		stopped = _count_and_stop_audio(get_tree().root)

	return {"ok": true, "stopped": stopped}


# Busca recursiva em toda a árvore (corrigido: antes só buscava filhos diretos da raiz)
func _find_audio_player(hint_path: String) -> Node:
	return _find_audio_recursive(get_tree().root, hint_path)


func _find_audio_recursive(node: Node, hint: String) -> Node:
	for child in node.get_children():
		if child is AudioStreamPlayer and (hint == "" or hint in child.get_path()):
			return child
		var found := _find_audio_recursive(child, hint)
		if found:
			return found
	return null


# Contagem iterativa (corrigido: GDScript int é value type, recursão com int não funciona)
func _count_and_stop_audio(root_node: Node) -> int:
	var count := 0
	var stack: Array[Node] = [root_node]
	while not stack.is_empty():
		var node := stack.pop_back()
		for child in node.get_children():
			if child is AudioStreamPlayer and child.playing:
				child.stop()
				count += 1
			stack.append(child)
	return count