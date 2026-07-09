@tool
extends EditorPlugin

# ── MCP IA DEV — Editor Plugin ──────────────────────────────────────
# Plugin do editor Godot que:
# 1. Abre TCPServer em localhost:<port> para comunicação com o MCP server
# 2. Exibe o painel "MCP IA DEV" no dock inferior com configurações
# Protocolo: JSON line-delimited (um JSON por linha, terminado em \n).

const CONFIG_PATH := "user://mcp_config.json"
const DEFAULT_PORT := 9080
const DEFAULT_GAME_PORT := 9081
const MAX_CONSOLE_LINES := 500
const MAX_LOG_ENTRIES := 100

var _server: TCPServer
var _client: StreamPeerTCP
var _port: int = DEFAULT_PORT
var _game_port: int = DEFAULT_GAME_PORT
var _running: bool = false
var _client_connected: bool = false
var _last_command_time: float = 0.0
var _command_log: Array[Dictionary] = []
var _console_lines: Array[String] = []
var _console_started: bool = false
var _dock: Control = null


# ── Lifecycle ───────────────────────────────────────────────────────

func _enter_tree() -> void:
	_load_full_config()
	_start_server()
	_add_dock()
	# Timer de polling TCP (50ms = 20 FPS, não todo frame)
	_poll_timer = Timer.new()
	_poll_timer.wait_time = 0.05
	_poll_timer.autostart = true
	_poll_timer.timeout.connect(_poll_tcp)
	add_child(_poll_timer)


func _exit_tree() -> void:
	if _poll_timer:
		_poll_timer.stop()
		_poll_timer.timeout.disconnect(_poll_tcp)
		_poll_timer.queue_free()
		_poll_timer = null
	_remove_dock()
	_stop_server()


# ── Server ──────────────────────────────────────────────────────────

func _start_server() -> void:
	_server = TCPServer.new()
	var err := _server.listen(_port, "127.0.0.1")
	if err != OK:
		_log("[MCP IA DEV] ERRO: não foi possível iniciar servidor na porta ", _port)
		return
	_running = true
	_log("[MCP IA DEV] Servidor TCP iniciado em localhost:", _port)
	_capture_console()


func _stop_server() -> void:
	_running = false
	if _client and _client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		_client.disconnect_from_host()
	if _server and _server.is_listening():
		_server.stop()
	_log("[MCP IA DEV] Servidor encerrado.")


# ── TCP Polling Timer (otimizado: NÃO roda todo frame) ──────────────
var _poll_timer: Timer


func _poll_tcp() -> void:
	if not _running:
		return

	# Aceita nova conexão
	if not _client or _client.get_status() != StreamPeerTCP.STATUS_CONNECTED:
		if _server and _server.is_connection_available():
			_client = _server.take_connection()
			_client_connected = true
			_last_command_time = Time.get_unix_time_from_system()
			_log("[MCP IA DEV] Cliente conectado.")

	# Detecta desconexão
	if _client and _client.get_status() != StreamPeerTCP.STATUS_CONNECTED and _client_connected:
		_client_connected = false
		_log("[MCP IA DEV] Cliente desconectado.")

	# Processa comandos
	if _client and _client.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		_process_client()


func _process_client() -> void:
	var available := _client.get_available_bytes()
	if available <= 0:
		return

	var data := _client.get_utf8_string(available)
	if not data or data.is_empty():
		return

	# Pode conter múltiplos comandos (um por linha)
	for line in data.split("\n"):
		if line.is_empty() or line[0] != "{":
			continue
		_log_command(line)
		var response := _handle_command(line)
		if not response.is_empty():
			_client.put_string(response + "\n")


# ── Command Handler ─────────────────────────────────────────────────

func _handle_command(raw: String) -> String:
	var json_conv = JSON.new()
	var err := json_conv.parse(raw)
	if err != OK:
		return _json_error("JSON inválido: " + raw)

	var cmd: Dictionary = json_conv.data
	var method: String = cmd.get("method", "")
	var params: Dictionary = cmd.get("params", {})
	var req_id = cmd.get("id", 0)

	match method:
		"ping":
			return _json_ok(req_id, {"pong": true, "editor_open": true})

		"get_editor_state":
			return _handle_get_editor_state(req_id, params)

		"take_screenshot":
			return _handle_take_screenshot(req_id, params)

		"run_scene":
			return _handle_run_scene(req_id, params)

		"stop_scene":
			return _handle_stop_scene(req_id, params)

		"read_console_since":
			return _handle_read_console_since(req_id, params)

		"hot_reload_script":
			return _handle_hot_reload_script(req_id, params)

		"rescan_filesystem":
			return _handle_rescan_filesystem(req_id, params)

		# ── GAP #12: Multi-Cena ──────────────────────────────
		"open_scene":
			return _handle_open_scene(req_id, params)

		# ── GAP #16: Tracking Cena Aberta ────────────────────
		"get_open_scenes":
			return _handle_get_open_scenes(req_id, params)

		# ── GAP #18: Seleção/Foco ────────────────────────────
		"select_node":
			return _handle_select_node(req_id, params)
		"frame_node":
			return _handle_frame_node(req_id, params)

		# ── MODO DIRETO: manipulação em tempo real ──
		"create_node":
			return _handle_create_node(req_id, params)
		"delete_node":
			return _handle_delete_node(req_id, params)
		"set_node_property":
			return _handle_set_node_property(req_id, params)
		"get_node_property":
			return _handle_get_node_property(req_id, params)
		"save_scene":
			return _handle_save_scene(req_id, params)
		"get_scene_tree":
			return _handle_get_scene_tree(req_id, params)

		_:
			return _json_error("Comando desconhecido: " + method, req_id)


# ── Command Implementations ─────────────────────────────────────────

func _handle_get_editor_state(req_id, _params: Dictionary) -> String:
	var state := {
		"editor_open": true,
		"current_scene": "",
		"scene_modified": false,
		"playing": EditorInterface.get_editor_scale(),  # dummy — real check via get_playing_scene
	}
	var edited := EditorInterface.get_edited_scene_root()
	if edited:
		state["current_scene"] = edited.scene_file_path
		state["scene_modified"] = edited.scene_file_path != ""  # simplified
	if EditorInterface.get_playing_scene() != null:
		state["playing"] = true
	return _json_ok(req_id, state)


func _handle_take_screenshot(req_id, _params: Dictionary) -> String:
	var viewport := EditorInterface.get_editor_viewport_2d()
	if not viewport:
		return _json_error("Viewport 2D não disponível", req_id)

	var img := viewport.get_texture().get_image()
	if not img:
		return _json_error("Falha ao capturar imagem do editor", req_id)

	# Salva em caminho temporário
	var path := "user://mcp_screenshot_%s.png" % Time.get_unix_time_from_system()
	var err := img.save_png(path)
	if err != OK:
		return _json_error("Falha ao salvar screenshot", req_id)

	# Converte para base64 para envio
	var file := FileAccess.open(path, FileAccess.READ)
	if not file:
		return _json_error("Falha ao ler screenshot salvo", req_id)
	var png_data := file.get_buffer(file.get_length())
	file.close()

	var base64 := Marshalls.raw_to_base64(png_data)
	return _json_ok(req_id, {
		"image_path": ProjectSettings.globalize_path(path),
		"image_base64": base64,
		"width": img.get_width(),
		"height": img.get_height(),
	})


func _handle_run_scene(req_id, params: Dictionary) -> String:
	var scene_path: String = params.get("scene_path", "")
	if scene_path.is_empty():
		EditorInterface.play_main_scene()
	else:
		EditorInterface.play_custom_scene(scene_path)
	return _json_ok(req_id, {"running": true})


func _handle_stop_scene(req_id, _params: Dictionary) -> String:
	EditorInterface.stop_playing_scene()
	return _json_ok(req_id, {"stopped": true})


func _handle_read_console_since(req_id, params: Dictionary) -> String:
	var since: float = params.get("since_timestamp", 0.0)
	var lines: Array[String] = []
	for line in _console_lines:
		lines.append(line)
	return _json_ok(req_id, {"lines": lines})


func _handle_hot_reload_script(req_id, params: Dictionary) -> String:
	var script_path: String = params.get("script_path", "")
	if script_path.is_empty():
		return _json_error("script_path é obrigatório", req_id)

	var res := load(script_path)
	if res:
		res.reload()
		return _json_ok(req_id, {"reloaded": script_path})
	return _json_error("Falha ao recarregar script: " + script_path, req_id)


func _handle_rescan_filesystem(req_id, _params: Dictionary) -> String:
	EditorInterface.get_resource_filesystem().scan()
	var edited := EditorInterface.get_edited_scene_root()
	if edited:
		EditorInterface.reload_scene_from_path(edited.scene_file_path)
	return _json_ok(req_id, {"rescanned": true})


# ── GAP #12: Multi-Cena ──────────────────────────────────────────────

func _handle_open_scene(req_id, params: Dictionary) -> String:
	var scene_path: String = params.get("scene_path", "")
	if scene_path.is_empty():
		return _json_error("scene_path obrigatorio.", req_id)

	EditorInterface.open_scene_from_path(scene_path)
	return _json_ok(req_id, {"opened": scene_path})


# ── GAP #16: Tracking Cena Aberta ────────────────────────────────────

func _handle_get_open_scenes(req_id, _params: Dictionary) -> String:
	var scenes: Array[String] = []
	var edited := EditorInterface.get_edited_scene_root()
	if edited:
		scenes.append(edited.scene_file_path)
	return _json_ok(req_id, {"open_scenes": scenes, "count": scenes.size()})


# ── GAP #18: Seleção e Foco de Nós ───────────────────────────────────

func _handle_select_node(req_id, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", "")
	if node_path.is_empty():
		return _json_error("node_path obrigatorio.", req_id)

	var root := EditorInterface.get_edited_scene_root()
	if not root:
		return _json_error("Nenhuma cena aberta.", req_id)

	var node := _find_node_by_path(root, node_path)
	if not node:
		return _json_error("No '%s' nao encontrado na cena aberta." % node_path, req_id)

	EditorInterface.get_selection().clear()
	EditorInterface.get_selection().add_node(node)
	return _json_ok(req_id, {"selected": node_path})


func _handle_frame_node(req_id, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", "")
	if node_path.is_empty():
		return _json_error("node_path obrigatorio.", req_id)

	var root := EditorInterface.get_edited_scene_root()
	if not root:
		return _json_error("Nenhuma cena aberta.", req_id)

	var node := _find_node_by_path(root, node_path)
	if not node:
		return _json_error("No '%s' nao encontrado." % node_path, req_id)

	# Foca no nó (expande a árvore e centraliza na viewport)
	EditorInterface.get_selection().clear()
	EditorInterface.get_selection().add_node(node)
	EditorInterface.edit_node(node)
	return _json_ok(req_id, {"framed": node_path})


# ── MODO DIRETO: manipulação em tempo real ───────────────────────────

func _find_node_by_path(root: Node, path: String) -> Node:
	if path == "." or path == "":
		return root
	var clean := path.trim_prefix("./")
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


func _handle_create_node(req_id: int, params: Dictionary) -> String:
	var parent_path: String = params.get("parent_path", ".")
	var node_name: String = params.get("node_name", "")
	var node_type: String = params.get("node_type", "Node")
	var properties: Dictionary = params.get("properties", {})

	var root := EditorInterface.get_edited_scene_root()
	if not root:
		return _json_error("Nenhuma cena aberta no editor.", req_id)
	if node_name.is_empty():
		return _json_error("node_name obrigatorio.", req_id)

	var parent := _find_node_by_path(root, parent_path)
	if not parent:
		return _json_error("No pai nao encontrado: " + parent_path, req_id)

	if not ClassDB.class_exists(node_type):
		return _json_error("Tipo de no invalido: " + node_type, req_id)

	var node: Node
	if ClassDB.can_instantiate(node_type):
		node = ClassDB.instantiate(node_type)
	else:
		return _json_error("Tipo nao pode ser instanciado: " + node_type, req_id)

	node.name = node_name
	for prop in properties:
		node.set(prop, properties[prop])

	parent.add_child(node)
	node.owner = root
	EditorInterface.mark_scene_as_unsaved()
	_log("[MCP IA DEV] No criado: " + node_name + " (" + node_type + ")")
	return _json_ok(req_id, {"created": node_name, "type": node_type})


func _handle_delete_node(req_id: int, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", "")
	var root := EditorInterface.get_edited_scene_root()
	if not root:
		return _json_error("Nenhuma cena aberta.", req_id)
	if node_path.is_empty() or node_path == ".":
		return _json_error("Nao pode deletar raiz.", req_id)

	var node := _find_node_by_path(root, node_path)
	if not node:
		return _json_error("No nao encontrado: " + node_path, req_id)

	var nome := node.name
	node.queue_free()
	EditorInterface.mark_scene_as_unsaved()
	return _json_ok(req_id, {"deleted": nome})


func _handle_set_node_property(req_id: int, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", ".")
	var property_name: String = params.get("property_name", "")
	var value_str: String = str(params.get("value", ""))

	var root := EditorInterface.get_edited_scene_root()
	if not root:
		return _json_error("Nenhuma cena aberta.", req_id)
	if property_name.is_empty():
		return _json_error("property_name obrigatorio.", req_id)

	var node := _find_node_by_path(root, node_path)
	if not node:
		return _json_error("No nao encontrado: " + node_path, req_id)

	var value = _parse_godot_value(value_str)
	node.set(property_name, value)
	EditorInterface.mark_scene_as_unsaved()
	return _json_ok(req_id, {"node": node_path, "property": property_name, "set": true})


func _handle_get_node_property(req_id: int, params: Dictionary) -> String:
	var node_path: String = params.get("node_path", ".")
	var property_name: String = params.get("property_name", "")

	var root := EditorInterface.get_edited_scene_root()
	if not root:
		return _json_error("Nenhuma cena aberta.", req_id)
	if property_name.is_empty():
		return _json_error("property_name obrigatorio.", req_id)

	var node := _find_node_by_path(root, node_path)
	if not node:
		return _json_error("No nao encontrado: " + node_path, req_id)

	var val = node.get(property_name)
	return _json_ok(req_id, {"node": node_path, "property": property_name, "value": str(val)})


func _handle_save_scene(req_id: int, _params: Dictionary) -> String:
	var root := EditorInterface.get_edited_scene_root()
	if not root:
		return _json_error("Nenhuma cena aberta.", req_id)
	var err := EditorInterface.save_scene()
	if err == OK:
		return _json_ok(req_id, {"saved": true})
	return _json_error("Erro ao salvar: " + str(err), req_id)


func _handle_get_scene_tree(req_id: int, _params: Dictionary) -> String:
	var root := EditorInterface.get_edited_scene_root()
	if not root:
		return _json_ok(req_id, {"scene": "", "nodes": []})

	# Coleta simplificada: apenas nomes e tipos
	var node_list: Array = []
	_collect_simple(root, node_list)
	return _json_ok(req_id, {"scene": root.scene_file_path, "nodes": node_list})


func _collect_simple(node: Node, arr: Array) -> void:
	arr.append({"n": node.name, "t": node.get_class()})
	for child in node.get_children():
		_collect_simple(child, arr)


func _parse_godot_value(raw: String):
	raw = raw.strip_edges()
	if raw.begins_with("Vector2(") and raw.ends_with(")"):
		var inner := raw.trim_prefix("Vector2(").trim_suffix(")")
		var parts := inner.split(",")
		if parts.size() >= 2:
			return Vector2(float(parts[0]), float(parts[1]))
	if raw.begins_with("Color(") and raw.ends_with(")"):
		var inner := raw.trim_prefix("Color(").trim_suffix(")")
		var parts := inner.split(",")
		if parts.size() >= 3:
			return Color(float(parts[0]), float(parts[1]), float(parts[2]))
	if raw.begins_with("#") and raw.length() == 7:
		return Color(raw)
	if raw == "true": return true
	if raw == "false": return false
	if raw.is_valid_int(): return int(raw)
	if raw.is_valid_float(): return float(raw)
	return raw


# ── Console Capture ─────────────────────────────────────────────────

func _log(msg1: String, msg2 = "", msg3 = "") -> void:
	"""Substitui print() — armazena no buffer do console para a IA ler."""
	var full := str(msg1) + str(msg2) + str(msg3)
	_console_lines.append("[%s] %s" % [Time.get_time_string_from_system(), full])
	while _console_lines.size() > MAX_CONSOLE_LINES:
		_console_lines.pop_front()
	print(full)  # ainda exibe no console do editor


func _capture_console() -> void:
	_console_lines.append("[%s] Console MCP IA DEV ativo" % Time.get_time_string_from_system())


# ── JSON Helpers ────────────────────────────────────────────────────

func _json_ok(req_id, data: Dictionary) -> String:
	var response := {
		"jsonrpc": "2.0",
		"id": req_id,
		"result": data,
	}
	return JSON.stringify(response)


func _json_error(message: String, req_id = 0) -> String:
	var response := {
		"jsonrpc": "2.0",
		"id": req_id,
		"error": {"code": -1, "message": message},
	}
	return JSON.stringify(response)


# ── Dock ─────────────────────────────────────────────────────────────

func _add_dock() -> void:
	var dock_script := load("res://addons/mcp_bridge/mcp_dock.gd")
	if not dock_script:
		_log("[MCP IA DEV] ERRO: não foi possível carregar mcp_dock.gd")
		return

	_dock = dock_script.new()
	_dock.setup(self)
	add_control_to_bottom_panel(_dock, "MCP IA DEV")
	_log("[MCP IA DEV] Painel registrado no dock inferior.")


func _remove_dock() -> void:
	if _dock:
		remove_control_from_bottom_panel(_dock)
		_dock.queue_free()
		_dock = null


# ── Config ──────────────────────────────────────────────────────────

func _load_full_config() -> void:
	var cfg := _read_config_json()
	if cfg.is_empty():
		_port = DEFAULT_PORT
		_game_port = DEFAULT_GAME_PORT
		return

	_port = cfg.get("addon_port", DEFAULT_PORT)
	_game_port = cfg.get("game_port", DEFAULT_GAME_PORT)
	_log("[MCP IA DEV] Config carregada: editor=%d, game=%d" % [_port, _game_port])


func _reload_config() -> void:
	"""Chamado pelo dock após salvar config."""
	_load_full_config()
	_log("[MCP IA DEV] Configuração recarregada.")


# ── Command Log ─────────────────────────────────────────────────────

func _log_command(raw: String) -> void:
	var json_conv := JSON.new()
	if json_conv.parse(raw) != OK:
		return
	var cmd: Dictionary = json_conv.data
	var method: String = cmd.get("method", "?")
	var now := Time.get_time_string_from_system()
	_last_command_time = Time.get_unix_time_from_system()

	_command_log.append({
		"time": now,
		"method": method,
	})

	# Limita tamanho do log
	while _command_log.size() > MAX_LOG_ENTRIES:
		_command_log.pop_front()


# ── Métodos públicos (chamados pelo dock) ────────────────────────────

func is_server_running() -> bool:
	return _running


func is_client_connected() -> bool:
	return _client_connected


func get_command_log() -> Array:
	return _command_log.duplicate()


func clear_command_log() -> void:
	_command_log.clear()


func get_project_info() -> Dictionary:
	var info := {
		"name": ProjectSettings.get_setting("application/config/name", "?"),
		"main_scene": ProjectSettings.get_setting("application/run/main_scene", ""),
		"renderer": ProjectSettings.get_setting("rendering/renderer/rendering_method", "?"),
		"path": ProjectSettings.globalize_path("res://"),
	}
	return info


func restart_server() -> void:
	_stop_server()
	_load_full_config()
	_start_server()
	_log("[MCP IA DEV] Servidor reiniciado.")


func get_editor_port() -> int:
	return _port


func get_game_port() -> int:
	return _game_port


func get_config_path() -> String:
	return CONFIG_PATH


func get_recent_projects() -> Array:
	"""Retorna lista de projetos recentes do Godot."""
	var cfg_path := OS.get_user_data_dir().path_join("../../Godot/projects.cfg")
	if not FileAccess.file_exists(cfg_path):
		return []

	var file := FileAccess.open(cfg_path, FileAccess.READ)
	if not file:
		return []

	var content := file.get_as_text()
	file.close()

	var projects: Array = []
	for line in content.split("\n"):
		var stripped := line.strip_edges()
		if stripped.begins_with("[") and stripped.ends_with("]"):
			var proj_path := stripped.substr(1, stripped.length() - 2)
			if proj_path.begins_with("C:") or proj_path.begins_with("/"):
				var proj_name := proj_path.get_file()
				var has_addon := FileAccess.file_exists(proj_path.path_join("addons/mcp_bridge/plugin.cfg"))
				projects.append({
					"path": proj_path,
					"name": proj_name,
					"has_mcp": has_addon,
				})

	return projects


func get_full_editor_state() -> Dictionary:
	var edited := EditorInterface.get_edited_scene_root()
	var playing := EditorInterface.get_playing_scene() != null
	return {
		"server_running": _running,
		"client_connected": _client_connected,
		"port": _port,
		"current_scene": edited.scene_file_path if edited else "",
		"scene_modified": edited.scene_file_path != "" if edited else false,
		"playing": playing,
		"command_count": _command_log.size(),
	}


func _read_config_json() -> Dictionary:
	if not FileAccess.file_exists(CONFIG_PATH):
		_log("[MCP IA DEV] config.json não encontrado, usando padrões.")
		return {}

	var file := FileAccess.open(CONFIG_PATH, FileAccess.READ)
	if not file:
		return {}

	var text := file.get_as_text()
	file.close()

	var json_conv := JSON.new()
	var err := json_conv.parse(text)
	if err != OK:
		_log("[MCP IA DEV] ERRO: config.json inválido.")
		return {}

	return json_conv.data
