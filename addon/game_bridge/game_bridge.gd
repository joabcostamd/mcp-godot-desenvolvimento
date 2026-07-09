extends Node

signal test_signal

# ── Game Bridge Autoload ─────────────────────────────────────────────
# TCPServer em localhost:9081. Comunica com o MCP server para injetar
# input, executar GDScript e observar sinais no jogo EM EXECUÇÃO.
#
# SEGURANÇA: só inicia se NÃO for build exportado (standalone).
# OS.has_feature("standalone") = true apenas em builds exportadas 
# (debug ou release). Falso no editor e em run_game --path.

const PORT := 9081
const MAX_CONSOLE := 200
const MAX_LOG_ENTRIES := 500

var _server: TCPServer
var _client: StreamPeerTCP
var _running: bool = false

# B2 FIX: Buffer de acumulacao para mensagens TCP fragmentadas
var _recv_buffer: String = ""

# ── GAP #6: Buffer circular de logs ──────────────────────────────────
var _log_buffer: Array[Dictionary] = []
var _log_index: int = 0
var _console_hooked: bool = false

# ── Lifecycle ────────────────────────────────────────────────────────

func _ready() -> void:
	if OS.has_feature("standalone"):
		return
	_start_server()
	_hook_console()
	# Test helper: periodic test_signal every 1.5s for watch_signal testing
	var timer := get_tree().create_timer(1.5)
	timer.timeout.connect(_emit_test_signal)

func _emit_test_signal() -> void:
	test_signal.emit()
	print("[GameBridge] test_signal emitted")
	var timer := get_tree().create_timer(1.5)
	timer.timeout.connect(_emit_test_signal)


func _exit_tree() -> void:
	_stop_server()


func _start_server() -> void:
	_server = TCPServer.new()
	var err := _server.listen(PORT, "127.0.0.1")
	if err != OK:
		print("[GameBridge] ERRO: porta ", PORT, " indisponível.")
		return
	_running = true
	print("[GameBridge] TCP server em localhost:", PORT)


func _stop_server() -> void:
	_running = false
	if _client and _client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		_client.disconnect_from_host()
	if _server and _server.is_listening():
		_server.stop()


func _process(_delta: float) -> void:
	if not _running:
		return
	
	# Accept new connections (replaces stale ones automatically)
	if _server and _server.is_connection_available():
		var old := _client
		_client = _server.take_connection()
		if old and old.get_status() == StreamPeerTCP.STATUS_CONNECTED:
			old.disconnect_from_host()
	
	if not _client or _client.get_status() != StreamPeerTCP.STATUS_CONNECTED:
		return
	
	_process_client()


# B2+B13 FIX: Buffer de acumulacao TCP + verificacao de put_data
func _process_client() -> void:
	var avail := _client.get_available_bytes()
	if avail <= 0:
		return

	var raw: Array = _client.get_data(avail)
	if raw[0] != OK:
		# B2: Conexao quebrada — limpa buffer e cliente
		_recv_buffer = ""
		_client = null
		return
	var chunk: String = raw[1].get_string_from_utf8()
	if chunk.is_empty():
		return

	_recv_buffer += chunk

	# Processa apenas linhas completas (terminadas em \n)
	while "\n" in _recv_buffer:
		var newline := _recv_buffer.find("\n")
		var line := _recv_buffer.substr(0, newline)
		_recv_buffer = _recv_buffer.substr(newline + 1)
		if line.is_empty() or line[0] != "{":
			continue
		var response := _handle_command(line)
		if not response.is_empty():
			# B13 FIX: Verifica retorno de put_data
			var put_err := _client.put_data((response + "\n").to_utf8_buffer())
			if put_err != OK:
				_add_log("error", "put_data falhou: codigo %d. Desconectando cliente." % put_err)
				_recv_buffer = ""
				_client = null
				return


# ── GAP #6: Console Hook (captura erros/warnings/prints) ─────────────

func _hook_console() -> void:
	if _console_hooked:
		return
	_console_hooked = true
	# Nota: Godot 4 não tem sinal global de log. Usamos uma abordagem
	# alternativa: timer que coleta erros acumulados.
	# Para erros em tempo real, _cmd_execute_gdscript faz parse direto.
	_add_log("info", "GameBridge iniciado. Buffer de logs ativo (%d entradas)." % MAX_LOG_ENTRIES)


func _add_log(level: String, message: String) -> void:
	var entry := {
		"index": _log_index,
		"time": Time.get_ticks_msec() / 1000.0,
		"level": level,  # "info", "warning", "error", "print"
		"message": message,
	}
	_log_buffer.append(entry)
	_log_index += 1
	# Mantém buffer limitado
	while _log_buffer.size() > MAX_LOG_ENTRIES:
		_log_buffer.pop_front()


func _capture_print(text: String) -> void:
	_add_log("print", text)


func _capture_error(text: String) -> void:
	_add_log("error", text)


func _capture_warning(text: String) -> void:
	_add_log("warning", text)


func _cmd_get_logs(req_id: int, params: Dictionary) -> String:
	var since_index: int = params.get("since_index", 0)
	var max_entries: int = params.get("max_entries", 100)
	var level_filter: String = params.get("level", "all")

	var result: Array[Dictionary] = []
	for entry in _log_buffer:
		if entry["index"] < since_index:
			continue
		if level_filter != "all" and entry["level"] != level_filter:
			continue
		result.append(entry)
		if result.size() >= max_entries:
			break

	return _json_ok(req_id, {
		"logs": result,
		"count": result.size(),
		"latest_index": _log_index,
		"total_buffered": _log_buffer.size(),
	})


# ── GAP #2: Hot Reload ────────────────────────────────────────────────

func _cmd_reload_resource(req_id: int, params: Dictionary) -> String:
	var resource_path: String = params.get("resource_path", "")
	if resource_path.is_empty():
		return _json_error("resource_path obrigatorio.", req_id)
	if not resource_path.begins_with("res://"):
		resource_path = "res://" + resource_path.lstrip("/")

	var res := load(resource_path)
	if res == null:
		_add_log("error", "reload_resource: recurso nao encontrado: " + resource_path)
		return _json_error("Recurso nao encontrado: " + resource_path, req_id)

	var err: int = res.reload()
	if err != OK:
		_add_log("error", "reload_resource: falha ao recarregar %s (codigo %d)" % [resource_path, err])
		return _json_error("Falha ao recarregar %s (erro %d)" % [resource_path, err], req_id)

	_add_log("info", "reload_resource: %s recarregado" % resource_path)

	# Se for script, re-aplica em todos os nos que usam
	if res is GDScript:
		var count := 0
		_reapply_script(get_tree().root, res, count)

	return _json_ok(req_id, {"reloaded": resource_path, "type": res.get_class()})


# B20 FIX: _reapply_script agora é verdadeiramente recursivo
func _reapply_script(root: Node, script: GDScript, count: int) -> void:
	for child in root.get_children():
		if child.get_script() == script:
			child.set_script(script)
		# Recursivo: processa filhos dos filhos
		if child.get_child_count() > 0:
			_reapply_script(child, script, count)


# ── Command Router ────────────────────────────────────────────────────

func _handle_command(raw: String) -> String:
	var json := JSON.new()
	if json.parse(raw) != OK:
		return _json_error("JSON inválido")

	var cmd: Dictionary = json.data
	var method: String = cmd.get("method", "")
	var params: Dictionary = cmd.get("params", {})
	var req_id = cmd.get("id", 0)

	match method:
		"ping":
			return _json_ok(req_id, {"pong": true, "running": _running})
		"inject_input":
			return _cmd_inject_input(req_id, params)
		"execute_gdscript":
			return _cmd_execute_gdscript(req_id, params)
		"watch_signal":
			return _cmd_watch_signal(req_id, params)
		"screenshot":
			return _cmd_screenshot(req_id, params)
		# ── GAP #6: Streaming de logs ──────────────────────────
		"get_logs":
			return _cmd_get_logs(req_id, params)
		# ── GAP #2: Hot Reload ────────────────────────────────
		"reload_resource":
			return _cmd_reload_resource(req_id, params)
		# ── GAP #3: MODO DIRETO no jogo rodando ────────────────────
		"get_scene_tree":
			return _cmd_get_scene_tree(req_id, params)
		"get_node_property":
			return _cmd_get_node_property(req_id, params)
		"set_node_property":
			return _cmd_set_node_property(req_id, params)
		"create_node":
			return _cmd_create_node(req_id, params)
		"delete_node":
			return _cmd_delete_node(req_id, params)
		# ── GAP #5: Hot-Patch Scripts ───────────────────────────
		"patch_method":
			return _cmd_patch_method(req_id, params)
		"inject_signal_handler":
			return _cmd_inject_signal_handler(req_id, params)
		# ── GAP #8: Input Recording ────────────────────────────
		"start_recording":
			return _cmd_start_recording(req_id, params)
		"stop_recording":
			return _cmd_stop_recording(req_id, params)
		"playback_recording":
			return _cmd_playback_recording(req_id, params)
		# ── GAP #11: Live REPL ─────────────────────────────────
		"repl_create":
			return _cmd_repl_create(req_id, params)
		"repl_eval":
			return _cmd_repl_eval(req_id, params)
		"repl_get":
			return _cmd_repl_get(req_id, params)
		"repl_destroy":
			return _cmd_repl_destroy(req_id, params)
		# ── GAP #9: Push Notifications ─────────────────────────
		"subscribe_signal":
			return _cmd_subscribe_signal(req_id, params)
		"get_pending_events":
			return _cmd_get_pending_events(req_id, params)
		# ── GAP #17: Debug Visual Runtime ─────────────────────
		"toggle_debug":
			return _cmd_toggle_debug(req_id, params)
		_:
			return _json_error("Comando desconhecido: " + method, req_id)


# ── inject_input ──────────────────────────────────────────────────────

func _cmd_inject_input(req_id: int, params: Dictionary) -> String:
	var event_type: String = params.get("type", "")
	var event_data: Dictionary = params.get("data", {})

	match event_type:
		"key":
			var ev := InputEventKey.new()
			ev.pressed = event_data.get("pressed", true)
			ev.keycode = event_data.get("keycode", 0)
			ev.echo = false
			Input.parse_input_event(ev)
			return _json_ok(req_id, {"injected": "key", "keycode": ev.keycode})

		"mouse_button":
			var ev := InputEventMouseButton.new()
			ev.pressed = event_data.get("pressed", true)
			ev.button_index = event_data.get("button_index", 1)
			ev.position = Vector2(event_data.get("x", 0), event_data.get("y", 0))
			Input.parse_input_event(ev)
			return _json_ok(req_id, {"injected": "mouse_button", "button": ev.button_index})

		"mouse_motion":
			var ev := InputEventMouseMotion.new()
			ev.position = Vector2(event_data.get("x", 0), event_data.get("y", 0))
			Input.parse_input_event(ev)
			return _json_ok(req_id, {"injected": "mouse_motion"})

		# ── GAP #7: Gamepad ──────────────────────────────────
		"joypad_button":
			var ev := InputEventJoypadButton.new()
			ev.device = event_data.get("device", 0)
			ev.button_index = event_data.get("button", 0)
			ev.pressed = event_data.get("pressed", true)
			ev.pressure = event_data.get("pressure", 1.0)
			Input.parse_input_event(ev)
			return _json_ok(req_id, {"injected": "joypad_button", "button": ev.button_index})

		"joypad_motion":
			var ev := InputEventJoypadMotion.new()
			ev.device = event_data.get("device", 0)
			ev.axis = event_data.get("axis", 0)
			ev.axis_value = event_data.get("value", 0.0)
			Input.parse_input_event(ev)
			return _json_ok(req_id, {"injected": "joypad_motion", "axis": ev.axis})

		# ── GAP #7: Touch ────────────────────────────────────
		"screen_touch":
			var ev := InputEventScreenTouch.new()
			ev.index = event_data.get("index", 0)
			ev.position = Vector2(event_data.get("x", 0), event_data.get("y", 0))
			ev.pressed = event_data.get("pressed", true)
			Input.parse_input_event(ev)
			return _json_ok(req_id, {"injected": "screen_touch", "index": ev.index})

		"screen_drag":
			var ev := InputEventScreenDrag.new()
			ev.index = event_data.get("index", 0)
			ev.position = Vector2(event_data.get("x", 0), event_data.get("y", 0))
			ev.relative = Vector2(event_data.get("dx", 0), event_data.get("dy", 0))
			Input.parse_input_event(ev)
			return _json_ok(req_id, {"injected": "screen_drag", "index": ev.index})

		_:
			return _json_error("Tipo de evento inválido: " + event_type, req_id)


# ── execute_gdscript ──────────────────────────────────────────────────

func _cmd_execute_gdscript(req_id: int, params: Dictionary) -> String:
	var code: String = params.get("code", "")
	if code.is_empty():
		return _json_error("Parametro 'code' vazio.", req_id)

	# B1 FIX: Tenta Expression primeiro (captura erros de runtime sem crash)
	# Expression só funciona com expressões puras; statements usam fallback
	var is_statement := false
	var stripped_first := code.strip_edges()
	for keyword in ["var ", "if ", "for ", "while ", "match ", "func ", "class ", "extends ", "signal ", "enum ", "const "]:
		if stripped_first.begins_with(keyword):
			is_statement = true
			break

	if not is_statement:
		var expr := Expression.new()
		var parse_err := expr.parse(code)
		if parse_err == OK:
			var result = expr.execute([], get_tree().root)
			if expr.has_execute_failed():
				_add_log("error", "[execute_gdscript:expression] Runtime error: %s | code: %s" % [expr.get_error_text(), code])
				return _json_error("Runtime error: %s" % expr.get_error_text(), req_id)
			_add_log("print", "[execute_gdscript:expression] %s -> %s" % [code, str(result) if result != null else "null"])
			return _json_ok(req_id, {"type": "expression", "value": str(result) if result != null else "null"})

	# Fallback: compila como statements (corpo de _execute)
	# Necessario para codigos como "var x = 42; return x"
	var indent := "\t"
	var indented_lines: Array[String] = []
	for raw_line in code.split("\n"):
		var stripped = raw_line.strip_edges()
		if stripped.is_empty():
			continue
		indented_lines.append(indent + stripped)

	var body := "\n".join(indented_lines)
	var wrapper := "extends Node\nfunc _execute():\n" + body

	var gd_script := GDScript.new()
	gd_script.source_code = wrapper
	var err := gd_script.reload()
	if err != OK:
		var stmt_error := _parse_gdscript_error(err, wrapper)
		_add_log("error", "[execute_gdscript] Erro: %s" % stmt_error)
		return _json_error("Erro de compilacao GDScript: %s" % stmt_error, req_id)

	# B1 FIX: Runtime error no call() - o node e removido mesmo se falhar
	var node := Node.new()
	node.set_script(gd_script)
	add_child(node)
	var result = null
	if node.has_method("_execute"):
		result = node.call("_execute")
	remove_child(node)
	node.free()
	_add_log("print", "[execute_gdscript:statement] %s -> %s" % [code.split("\n")[0] if code.length() > 0 else code, str(result) if result != null else "null"])
	return _json_ok(req_id, {"type": "statement", "value": str(result) if result != null else "null"})


# B12 FIX: Cobertura ampliada de erros de parse
func _parse_gdscript_error(err_code: int, source_code: String) -> String:
	match err_code:
		ERR_PARSE_ERROR:
			var lines := source_code.split("\n")
			for i in range(lines.size()):
				var l := lines[i].strip_edges()
				if l.begins_with("return (") and not l.ends_with(")"):
					return "Linha %d: parenteses nao fechados em '%s'" % [i + 1, l]
				if l.count("(") != l.count(")"):
					return "Linha %d: parenteses desbalanceados em '%s'" % [i + 1, l]
				if l.begins_with("if ") and ":" not in l:
					return "Linha %d: 'if' sem ':' em '%s'" % [i + 1, l]
				if l.begins_with("for ") and ":" not in l:
					return "Linha %d: 'for' sem ':' em '%s'" % [i + 1, l]
				if l.begins_with("func ") and ":" not in l:
					return "Linha %d: 'func' sem ':' em '%s'" % [i + 1, l]
				if l.begins_with("extends ") and "Node" not in l and "RefCounted" not in l and "Object" not in l and "Resource" not in l:
					if not ClassDB.class_exists(l.trim_prefix("extends ").strip_edges()):
						return "Linha %d: 'extends' invalido em '%s'" % [i + 1, l]
				# Indentacao inconsistente (tab vs spaces)
				var leading := lines[i].length() - lines[i].lstrip("\t").length()
				var spaces := lines[i].length() - lines[i].lstrip(" ").length()
				if leading == 0 and spaces > 0 and spaces % 4 != 0 and not l.is_empty() and not l.begins_with("#"):
					return "Linha %d: indentacao suspeita (use tabs) em '%s'" % [i + 1, l]
			# Fallback: mostra primeiras linhas problematicas
			var preview := ""
			for j in range(min(lines.size(), 5)):
				preview += "L%d: %s\n" % [j + 1, lines[j].strip_edges()]
			return "Erro de parse GDScript (codigo %d). Preview:\n%s" % [err_code, preview]
		ERR_COMPILATION_FAILED:
			return "Falha de compilacao GDScript (codigo %d)." % err_code
		_:
			return "Erro GDScript codigo %d." % err_code


# ── watch_signal ──────────────────────────────────────────────────────

func _cmd_watch_signal(req_id: int, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", "")
	var signal_name: String = params.get("signal_name", "")
	var timeout_sec: float = params.get("timeout", 5.0)

	if node_path.is_empty() or signal_name.is_empty():
		return _json_error("'node_path' e 'signal_name' obrigatorios.", req_id)

	var target := get_node_or_null(node_path)
	if not target:
		return _json_error("No '%s' nao encontrado." % node_path, req_id)

	if not target.has_signal(signal_name):
		return _json_error("Sinal '%s' nao existe no no '%s'." % [signal_name, node_path], req_id)

	# Non-blocking: callback one-shot + timer.
	# NOTA: usamos Dictionary como container mutavel porque closures em
	# GDScript capturam variaveis locais por copia (nao por referencia).
	var state := {"fired": false}

	# B9 FIX: Timer declarado ANTES do callback para evitar erro de escopo
	var timer := get_tree().create_timer(timeout_sec)

	var _cb := func(_arg1 = null):
		state["fired"] = true
		# B9 FIX: Forca disparo imediato do timer quando sinal chega
		timer.time_left = 0.0

	target.connect(signal_name, _cb, CONNECT_ONE_SHOT)

	var _on_timeout := func():
		var response := _json_ok(req_id, {"fired": state["fired"], "signal": signal_name})
		# B9+B13 FIX: Verifica cliente ANTES de enviar
		if _client and _client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
			var put_err := _client.put_data((response + "\n").to_utf8_buffer())
			if put_err != OK:
				_add_log("error", "watch_signal: put_data falhou (cliente desconectado)")
	timer.timeout.connect(_on_timeout)

	return ""  # Resposta enviada pelo callback do timer


# ── screenshot ─────────────────────────────────────────────────────────

func _cmd_screenshot(req_id: int, params: Dictionary) -> String:
	var filename: String = params.get("filename", "bridge_shot.png")
	var path := "user://" + filename
	# B11 FIX: Null check no get_texture() (pode ser null no primeiro frame)
	var tex := get_viewport().get_texture()
	if not tex:
		return _json_error("Viewport ainda nao renderizou. Tente novamente em alguns frames.", req_id)
	var img := tex.get_image()
	var err := img.save_png(path)
	if err == OK:
		return _json_ok(req_id, {"saved": path, "size": img.get_size()})
	else:
		return _json_error("Erro ao salvar PNG: " + str(err), req_id)


# ── GAP #3: MODO DIRETO no jogo rodando ───────────────────────────────
# Permite manipular a árvore de cena do jogo EM EXECUÇÃO,
# exatamente como o Modo Direto faz no editor.
# Isso unifica os dois canais: o MCP agora pode ler e modificar
# propriedades, criar/deletar nós e inspecionar a cena no jogo rodando.

func _find_node_by_path(root: Node, path: String) -> Node:
	if path == "." or path == "":
		return root
	var clean := path.trim_prefix("./")
	# Godot path convention: /root/X means "X under scene tree root (Window)"
	if clean.begins_with("/root/"):
		clean = clean.trim_prefix("/root/")
	elif clean == "/root":
		return root
	var parts := clean.split("/")
	var current := root
	for part in parts:
		if part.is_empty():
			continue
		var found := current.get_node_or_null(part)
		if not found:
			return null
		current = found
	return current


func _collect_nodes(node: Node) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for child in node.get_children():
		var entry := {
			"name": child.name,
			"type": child.get_class(),
			"children": _collect_nodes(child)
		}
		result.append(entry)
	return result


func _parse_godot_value(raw: String):
	# Vector2(x, y)
	if raw.begins_with("Vector2("):
		var inner := raw.trim_prefix("Vector2(").trim_suffix(")")
		var parts := inner.split(",")
		return Vector2(float(parts[0]), float(parts[1]))
	# Vector3(x, y, z)
	if raw.begins_with("Vector3("):
		var inner := raw.trim_prefix("Vector3(").trim_suffix(")")
		var parts := inner.split(",")
		return Vector3(float(parts[0]), float(parts[1]), float(parts[2]))
	# Color(r, g, b, a)
	if raw.begins_with("Color("):
		var inner := raw.trim_prefix("Color(").trim_suffix(")")
		var parts := inner.split(",")
		return Color(float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]))
	# Rect2(x, y, w, h)
	if raw.begins_with("Rect2("):
		var inner := raw.trim_prefix("Rect2(").trim_suffix(")")
		var parts := inner.split(",")
		return Rect2(float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]))
	# Transform2D(xx, xy, yx, yy, ox, oy)
	if raw.begins_with("Transform2D("):
		var inner := raw.trim_prefix("Transform2D(").trim_suffix(")")
		var parts := inner.split(",")
		return Transform2D(
			Vector2(float(parts[0]), float(parts[1])),
			Vector2(float(parts[2]), float(parts[3])),
			Vector2(float(parts[4]), float(parts[5])))
	# bool
	if raw == "true": return true
	if raw == "false": return false
	# int
	if raw.is_valid_int(): return int(raw)
	# float
	if raw.is_valid_float(): return float(raw)
	# string (default)
	return raw


func _serialize_value(val) -> String:
	if typeof(val) == TYPE_VECTOR2:
		return "Vector2(%s, %s)" % [val.x, val.y]
	if typeof(val) == TYPE_VECTOR3:
		return "Vector3(%s, %s, %s)" % [val.x, val.y, val.z]
	if typeof(val) == TYPE_COLOR:
		return "Color(%s, %s, %s, %s)" % [val.r, val.g, val.b, val.a]
	if typeof(val) == TYPE_RECT2:
		return "Rect2(%s, %s, %s, %s)" % [val.position.x, val.position.y, val.size.x, val.size.y]
	if typeof(val) == TYPE_TRANSFORM2D:
		return "Transform2D(%s, %s, %s, %s, %s, %s)" % [val.x.x, val.x.y, val.y.x, val.y.y, val.origin.x, val.origin.y]
	if typeof(val) == TYPE_BOOL:
		return "true" if val else "false"
	if typeof(val) == TYPE_INT or typeof(val) == TYPE_FLOAT:
		return str(val)
	return str(val)


func _cmd_get_scene_tree(req_id: int, _params: Dictionary) -> String:
	var root := get_tree().root
	var tree := _collect_nodes(root)
	return _json_ok(req_id, {"scene_tree": tree, "node_count": root.get_child_count()})


func _cmd_get_node_property(req_id: int, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", "")
	var property_name: String = params.get("property_name", "")
	if node_path.is_empty() or property_name.is_empty():
		return _json_error("node_path e property_name obrigatorios.", req_id)

	var node := _find_node_by_path(get_tree().root, node_path)
	if not node:
		return _json_error("No '%s' nao encontrado no jogo." % node_path, req_id)

	var val = node.get(property_name)
	return _json_ok(req_id, {"property": property_name, "value": _serialize_value(val)})


func _cmd_set_node_property(req_id: int, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", "")
	var property_name: String = params.get("property_name", "")
	var value_str: String = params.get("value", "")
	if node_path.is_empty() or property_name.is_empty():
		return _json_error("node_path e property_name obrigatorios.", req_id)

	var node := _find_node_by_path(get_tree().root, node_path)
	if not node:
		return _json_error("No '%s' nao encontrado no jogo." % node_path, req_id)

	var parsed = _parse_godot_value(value_str)
	node.set(property_name, parsed)
	return _json_ok(req_id, {"node": node_path, "property": property_name, "set_to": value_str})


func _cmd_create_node(req_id: int, params: Dictionary) -> String:
	var parent_path: String = params.get("parent_path", ".")
	var node_name: String = params.get("node_name", "")
	var node_type: String = params.get("node_type", "Node")
	var properties: Dictionary = params.get("properties", {})

	var root := get_tree().root
	var parent := _find_node_by_path(root, parent_path)
	if not parent:
		return _json_error("No pai '%s' nao encontrado no jogo." % parent_path, req_id)
	if node_name.is_empty():
		return _json_error("node_name obrigatorio.", req_id)
	if not ClassDB.class_exists(node_type):
		return _json_error("Tipo de no invalido: " + node_type, req_id)

	var new_node := ClassDB.instantiate(node_type) as Node
	if not new_node:
		return _json_error("Falha ao instanciar: " + node_type, req_id)

	new_node.name = node_name
	parent.add_child(new_node)

	if not properties.is_empty():
		for prop in properties:
			new_node.set(prop, _parse_godot_value(str(properties[prop])))

	return _json_ok(req_id, {"created": "%s/%s" % [parent_path, node_name], "type": node_type})


func _cmd_delete_node(req_id: int, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", "")
	if node_path.is_empty():
		return _json_error("node_path obrigatorio.", req_id)

	var node := _find_node_by_path(get_tree().root, node_path)
	if not node:
		return _json_error("No '%s' nao encontrado no jogo." % node_path, req_id)

	node.queue_free()
	return _json_ok(req_id, {"deleted": node_path})


# ── GAP #5: Hot-Patch Scripts ─────────────────────────────────────────
# Permite modificar métodos e injetar callbacks no jogo rodando,
# sem reiniciar. Complementa o Hot Reload (GAP #2) permitindo
# mudanças cirúrgicas em métodos específicos.

func _cmd_patch_method(req_id: int, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", "")
	var method_name: String = params.get("method_name", "")
	var new_code: String = params.get("new_code", "")

	if node_path.is_empty() or method_name.is_empty() or new_code.is_empty():
		return _json_error("node_path, method_name e new_code obrigatorios.", req_id)

	var node := _find_node_by_path(get_tree().root, node_path)
	if not node:
		return _json_error("No '%s' nao encontrado." % node_path, req_id)

	var script := node.get_script() as GDScript
	if not script:
		return _json_error("No '%s' nao tem script anexado." % node_path, req_id)

	var source := script.source_code
	if source.is_empty():
		return _json_error("Script sem source_code acessivel.", req_id)

	var lines := source.split("\n")
	var pattern := "func " + method_name + "("
	var method_line := -1
	var next_func_line := lines.size()

	# Encontra a linha do metodo
	for i in range(lines.size()):
		var stripped := lines[i].strip_edges()
		if pattern in stripped and not stripped.begins_with("#"):
			method_line = i
			break

	if method_line < 0:
		return _json_error("Metodo '%s' nao encontrado." % method_name, req_id)

	# B5 FIX: Detecta proximo metodo por indentacao, nao por 'func ' na linha
	# (evita quebrar em closures/funcoes aninhadas)
	var method_indent := -1
	for i in range(lines.size()):
		if i >= method_line:
			var stripped := lines[i].strip_edges()
			var leading := lines[i].length() - lines[i].lstrip("\t").length()
			if method_indent == -1 and i > method_line:
				# Primeira linha apos assinatura define a indentacao base
				for j in range(method_line + 1, lines.size()):
					var sj := lines[j].strip_edges()
					if not sj.is_empty() and not sj.begins_with("#"):
						method_indent = lines[j].length() - lines[j].lstrip("\t").length()
						break
				if method_indent == -1:
					method_indent = 0
			# Proximo metodo no MESMO nivel de indentacao (ou menos)
			if i > method_line and stripped.begins_with("func ") and not stripped.begins_with("#"):
				var func_indent := lines[i].length() - lines[i].lstrip("\t").length()
				if func_indent <= method_indent:
					next_func_line = i
					break

	# Extrai assinatura original
	var sig_line := lines[method_line].strip_edges()
	var paren_open := sig_line.find("(")
	var paren_close := sig_line.find(")")
	var sig_params := ""
	if paren_open != -1 and paren_close != -1:
		sig_params = sig_line.substr(paren_open, paren_close - paren_open + 1)
	else:
		sig_params = "()"

	# Constroi novo metodo
	var new_method := "func " + method_name + sig_params + ":\n"
	for code_line in new_code.split("\n"):
		new_method += "\t" + code_line.strip_edges() + "\n"

	# Substitui no source
	var new_source := ""
	for i in range(lines.size()):
		if i == method_line:
			new_source += new_method
		elif i > method_line and i < next_func_line:
			continue  # pula corpo antigo
		else:
			new_source += lines[i] + "\n"

	# Compila e aplica
	var new_script := GDScript.new()
	new_script.source_code = new_source
	var err := new_script.reload()
	if err != OK:
		_add_log("error", "patch_method: erro %d ao compilar" % err)
		return _json_error("Erro de compilacao GDScript (codigo %d)." % err, req_id)

	node.set_script(new_script)
	_add_log("info", "patch_method: %s.%s atualizado" % [node_path, method_name])
	return _json_ok(req_id, {"patched": "%s.%s" % [node_path, method_name]})


# B8 FIX: Dicionario de handlers injetados (evita orphans)
var _injected_handlers: Dictionary = {}  # handler_id -> {node, handler_node}

func _cmd_inject_signal_handler(req_id: int, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", "")
	var signal_name: String = params.get("signal_name", "")
	var handler_code: String = params.get("handler_code", "")

	if node_path.is_empty() or signal_name.is_empty() or handler_code.is_empty():
		return _json_error("node_path, signal_name e handler_code obrigatorios.", req_id)

	var node := _find_node_by_path(get_tree().root, node_path)
	if not node:
		return _json_error("No '%s' nao encontrado." % node_path, req_id)

	if not node.has_signal(signal_name):
		return _json_error("Sinal '%s' nao existe no no '%s'." % [signal_name, node_path], req_id)

	# Cria um script com uma funcao callback
	var script := GDScript.new()
	var code := "extends Node\nfunc _handler(_arg1 = null, _arg2 = null, _arg3 = null, _arg4 = null):\n\t%s\n" % handler_code.replace("\n", "\n\t")

	script.source_code = code
	var err := script.reload()
	if err != OK:
		return _json_error("Erro ao compilar handler GDScript (codigo %d)." % err, req_id)

	# B8 FIX: Nome unico + armazenamento no dicionario
	var handler_id := "signal_handler_%d" % randi()
	var handler_node := Node.new()
	handler_node.name = handler_id
	handler_node.set_script(script)
	add_child(handler_node)

	# Conecta o sinal
	var callable := Callable(handler_node, "_handler")
	node.connect(signal_name, callable)

	_injected_handlers[handler_id] = {"node_path": node_path, "signal": signal_name, "handler_node": handler_node}

	_add_log("info", "inject_signal_handler: %s.%s conectado (id=%s)" % [node_path, signal_name, handler_id])

	return _json_ok(req_id, {
		"injected": "%s.%s" % [node_path, signal_name],
		"handler_id": handler_id,
		"note": "Handler injetado. Use delete_node com o handler_id para remover.",
	})


# ── GAP #8: Input Recording ───────────────────────────────────────────

var _recording: bool = false
var _recorded_events: Array[Dictionary] = []
var _record_start_time: float = 0.0

func _cmd_start_recording(req_id: int, _params: Dictionary) -> String:
	_recording = true
	_recorded_events.clear()
	_record_start_time = Time.get_ticks_msec() / 1000.0
	_add_log("info", "Gravacao de input iniciada.")
	return _json_ok(req_id, {"recording": true})


func _cmd_stop_recording(req_id: int, _params: Dictionary) -> String:
	_recording = false
	var events_copy := _recorded_events.duplicate(true)
	_add_log("info", "Gravacao parada. %d eventos capturados." % events_copy.size())
	return _json_ok(req_id, {"recording": false, "events": events_copy, "count": events_copy.size()})


func _cmd_playback_recording(req_id: int, params: Dictionary) -> String:
	var events: Array = params.get("events", [])
	if events.is_empty():
		return _json_error("Nenhum evento para reproduzir.", req_id)

	var speed: float = params.get("speed", 1.0)
	_play_events(events, speed)
	return _json_ok(req_id, {"playing": true, "count": events.size(), "speed": speed})


func _play_events(events: Array, speed: float) -> void:
	var t0: float = _recorded_events[0].get("time", 0.0) if _recorded_events.size() > 0 else 0.0
	for i in range(events.size()):
		var evt: Dictionary = events[i]
		var delay: float = evt.get("time", 0.0) - t0
		var timer: SceneTreeTimer = get_tree().create_timer(delay / speed)
		var capture_i: int = i
		timer.timeout.connect(func():
			_inject_recorded_event(events[capture_i])
		)


func _inject_recorded_event(evt: Dictionary) -> void:
	var etype: String = evt.get("type", "")
	var data: Dictionary = evt.get("data", {})
	match etype:
		"key":
			var ev := InputEventKey.new()
			ev.pressed = data.get("pressed", true)
			ev.keycode = data.get("keycode", 0)
			Input.parse_input_event(ev)
		"mouse_button":
			var ev := InputEventMouseButton.new()
			ev.pressed = data.get("pressed", true)
			ev.button_index = data.get("button_index", 1)
			ev.position = Vector2(data.get("x", 0), data.get("y", 0))
			Input.parse_input_event(ev)
		"joypad_button":
			var ev := InputEventJoypadButton.new()
			ev.button_index = data.get("button", 0)
			ev.pressed = data.get("pressed", true)
			Input.parse_input_event(ev)


func _input(event: InputEvent) -> void:
	if not _recording:
		return
	var t := Time.get_ticks_msec() / 1000.0 - _record_start_time
	var entry: Dictionary
	if event is InputEventKey:
		entry = {"time": t, "type": "key", "data": {"keycode": event.keycode, "pressed": event.pressed}}
	elif event is InputEventMouseButton:
		entry = {"time": t, "type": "mouse_button", "data": {"button_index": event.button_index, "pressed": event.pressed, "x": event.position.x, "y": event.position.y}}
	elif event is InputEventJoypadButton:
		entry = {"time": t, "type": "joypad_button", "data": {"button": event.button_index, "pressed": event.pressed}}
	else:
		return
	_recorded_events.append(entry)


# ── GAP #11: Live REPL ────────────────────────────────────────────────

var _repl_node: Node = null

func _cmd_repl_create(req_id: int, _params: Dictionary) -> String:
	if _repl_node:
		return _json_ok(req_id, {"repl": "already_exists", "node": str(_repl_node.get_instance_id())})

	var script := GDScript.new()
	script.source_code = "extends Node\n"
	var err := script.reload()
	if err != OK:
		return _json_error("Falha ao criar script REPL.", req_id)

	_repl_node = Node.new()
	_repl_node.set_script(script)
	add_child(_repl_node)
	_add_log("info", "REPL criado.")
	return _json_ok(req_id, {"repl": "created", "node": str(_repl_node.get_instance_id())})


func _cmd_repl_eval(req_id: int, params: Dictionary) -> String:
	if not _repl_node:
		return _json_error("REPL nao iniciado. Use repl_create primeiro.", req_id)

	var code: String = params.get("code", "")
	if code.is_empty():
		return _json_error("code obrigatorio.", req_id)

	var script := _repl_node.get_script() as GDScript
	var source := script.source_code

	# Detecta se e statement ou expressao
	var is_statement := false
	var stripped := code.strip_edges()
	if stripped.begins_with("var ") or stripped.begins_with("if ") or stripped.begins_with("for ") or stripped.begins_with("while ") or stripped.begins_with("match "):
		is_statement = true

	var method_body := ""
	if is_statement:
		# Statements: corpo direto (sem return wrapper)
		method_body = "\t" + code.replace("\n", "\n\t")
	else:
		# Expressoes: return wrapper
		method_body = "\treturn (%s)" % code

	# Substitui ou adiciona metodo _repl_eval
	if "func _repl_eval(" in source:
		var lines := source.split("\n")
		var new_source := ""
		var skip := false
		for line in lines:
			if "func _repl_eval(" in line:
				new_source += "func _repl_eval():\n" + method_body + "\n"
				skip = true
			elif skip and line.begins_with("func "):
				new_source += line + "\n"
				skip = false
			elif not skip:
				new_source += line + "\n"
		source = new_source
	else:
		source += "\nfunc _repl_eval():\n" + method_body + "\n"

	script.source_code = source
	var err := script.reload()
	if err != OK:
		return _json_error("Erro ao compilar codigo REPL (codigo %d)." % err, req_id)

	_repl_node.set_script(script)
	var result = _repl_node.call("_repl_eval")
	_add_log("print", "[REPL] %s → %s" % [code, str(result) if result != null else "null"])
	return _json_ok(req_id, {"value": str(result) if result != null else "null"})


func _cmd_repl_get(req_id: int, params: Dictionary) -> String:
	if not _repl_node:
		return _json_error("REPL nao iniciado.", req_id)
	var var_name: String = params.get("var_name", "")
	if var_name.is_empty():
		return _json_error("var_name obrigatorio.", req_id)
	var val = _repl_node.get(var_name)
	return _json_ok(req_id, {"var": var_name, "value": _serialize_value(val) if val != null else "null"})


func _cmd_repl_destroy(req_id: int, _params: Dictionary) -> String:
	if _repl_node:
		_repl_node.queue_free()
		_repl_node = null
		_add_log("info", "REPL destruido.")
		return _json_ok(req_id, {"repl": "destroyed"})
	return _json_ok(req_id, {"repl": "not_found"})


# ── GAP #9: Push Notifications ────────────────────────────────────────

var _pending_events: Array[Dictionary] = []
var _subscriptions: Dictionary = {}  # signal_key -> bool

func _cmd_subscribe_signal(req_id: int, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", "")
	var signal_name: String = params.get("signal_name", "")

	if node_path.is_empty() or signal_name.is_empty():
		return _json_error("node_path e signal_name obrigatorios.", req_id)

	var node := _find_node_by_path(get_tree().root, node_path)
	if not node:
		return _json_error("No '%s' nao encontrado." % node_path, req_id)
	if not node.has_signal(signal_name):
		return _json_error("Sinal '%s' nao existe." % signal_name, req_id)

	var key := "%s::%s" % [node_path, signal_name]
	if _subscriptions.has(key):
		return _json_ok(req_id, {"subscribed": key, "note": "Ja inscrito."})

	_subscriptions[key] = true

	# B14 FIX: Callback captura ate 4 argumentos (cobre maioria dos sinais Godot)
	var _cb := func(arg1 = null, arg2 = null, arg3 = null, arg4 = null):
		var captured := []
		if arg1 != null: captured.append(str(arg1))
		if arg2 != null: captured.append(str(arg2))
		if arg3 != null: captured.append(str(arg3))
		if arg4 != null: captured.append(str(arg4))
		_pending_events.append({
			"node": node_path,
			"signal": signal_name,
			"args": ",".join(captured) if captured.size() > 0 else "null",
			"time": Time.get_ticks_msec() / 1000.0
		})

	# Tenta conectar com numero variavel de argumentos
	node.connect(signal_name, _cb)

	_add_log("info", "subscribe: %s" % key)
	return _json_ok(req_id, {"subscribed": key})


func _cmd_get_pending_events(req_id: int, _params: Dictionary) -> String:
	var events := _pending_events.duplicate(true)
	_pending_events.clear()
	return _json_ok(req_id, {"events": events, "count": events.size()})


# ── GAP #17: Debug Visual Runtime ─────────────────────────────────────

var _debug_states := {
	"collisions": false,
	"navigation": false,
	"paths": false,
}

func _cmd_toggle_debug(req_id: int, params: Dictionary) -> String:
	var what: String = params.get("what", "collisions")
	var enable: bool = params.get("enable", true)

	# B10 FIX: Usa bitwise OR para combinar flags, nao atribuicao direta
	var current := get_viewport().debug_draw
	match what:
		"collisions":
			_debug_states["collisions"] = enable
			get_viewport().debug_draw = (current | 1) if enable else (current & ~1)
		"navigation":
			_debug_states["navigation"] = enable
			get_viewport().debug_draw = (current | 2) if enable else (current & ~2)
		"paths":
			_debug_states["paths"] = enable
			get_viewport().debug_draw = (current | 4) if enable else (current & ~4)
		_:
			return _json_error("Debug type invalido: " + what + ". Use: collisions, navigation, paths.", req_id)

	_add_log("info", "toggle_debug: %s=%s" % [what, "ON" if enable else "OFF"])
	return _json_ok(req_id, {"debug": what, "enabled": enable, "states": _debug_states.duplicate()})


# ── JSON Helpers ──────────────────────────────────────────────────────

func _json_ok(req_id: int, data: Dictionary) -> String:
	var response := {"jsonrpc": "2.0", "id": req_id, "result": data}
	return JSON.stringify(response)


func _json_error(message: String, req_id: int = 0) -> String:
	var response := {"jsonrpc": "2.0", "id": req_id, "error": {"code": -1, "message": message}}
	return JSON.stringify(response)
