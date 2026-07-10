; mcp_addon.gd — Addon GDScript para MCP Godot (Fase 2B / A1)
;
; EditorPlugin que hospeda um WebSocket server para receber comandos
; do servidor Python e executar operações no editor com UndoRedo nativo.
;
; Baseado no padrão yurineko73/godot-mcp-native.
; Porta: 9082 | Protocolo: JSON-RPC 2.0 sobre WebSocket
;
; Instalação: copie esta pasta para addons/mcp_addon/ no projeto Godot.

@tool
extends EditorPlugin

const PORT = 9082
const MAX_CONNECTIONS = 1

var _server: TCPServer
var _peer: StreamPeerTCP = null
var _ws_server: WebSocketPeer
var _connected: bool = false
var _undo_redo: EditorUndoRedoManager


# ── Lifecycle ───────────────────────────────────────────────────────

func _enter_tree() -> void:
	_undo_redo = get_undo_redo()
	_start_server()
	print("[MCP Addon] Iniciado na porta ", PORT)


func _exit_tree() -> void:
	_stop_server()
	print("[MCP Addon] Encerrado")


func _process(_delta: float) -> void:
	if not _server:
		return

	# Aceita nova conexão
	if not _peer and _server.is_connection_available():
		_peer = _server.take_connection()
		_ws_server = WebSocketPeer.new()
		_ws_server.accept_stream(_peer)
		print("[MCP Addon] Cliente conectado")
		_connected = true

	# Processa mensagens
	if _ws_server and _ws_server.get_available_packet_count() > 0:
		var packet = _ws_server.get_packet()
		var message = packet.get_string_from_utf8()
		_handle_message(message)

	# Verifica desconexão
	if _ws_server and _ws_server.get_ready_state() == WebSocketPeer.STATE_CLOSED:
		_peer = null
		_ws_server = null
		_connected = false
		print("[MCP Addon] Cliente desconectado")


# ── Server ──────────────────────────────────────────────────────────

func _start_server() -> void:
	_server = TCPServer.new()
	if _server.listen(PORT) != OK:
		push_error("[MCP Addon] Falha ao iniciar servidor na porta ", PORT)
		_server = null


func _stop_server() -> void:
	if _peer:
		_peer = null
	if _server:
		_server.stop()
		_server = null
	_connected = false


# ── Message Handling ────────────────────────────────────────────────

func _handle_message(raw: String) -> void:
	var json = JSON.new()
	var err = json.parse(raw)
	if err != OK:
		_send_error(-32700, "Parse error: " + json.get_error_message())
		return

	var request = json.get_data()
	if not request is Dictionary:
		_send_error(-32600, "Invalid Request")
		return

	var method = request.get("method", "")
	var params = request.get("params", {})
	var req_id = request.get("id", null)

	match method:
		"ping":
			_send_result(req_id, {"status": "ok", "message": "pong"})
		"create_node":
			_create_node(req_id, params)
		"delete_node":
			_delete_node(req_id, params)
		"set_node_property":
			_set_node_property(req_id, params)
		"reparent_node":
			_reparent_node(req_id, params)
		"duplicate_node":
			_duplicate_node(req_id, params)
		"batch_edit":
			_batch_edit(req_id, params)
		"take_screenshot":
			_take_screenshot(req_id, params)
		"get_scene_tree":
			_get_scene_tree(req_id, params)
		_:
			_send_error(-32601, "Method not found: " + method, req_id)


# ── JSON-RPC Helpers ────────────────────────────────────────────────

func _send_result(id, result: Dictionary) -> void:
	_send({
		"jsonrpc": "2.0",
		"id": id,
		"result": result
	})


func _send_error(code: int, message: String, id = null) -> void:
	_send({
		"jsonrpc": "2.0",
		"id": id,
		"error": {
			"code": code,
			"message": message
		}
	})


func _send(data: Dictionary) -> void:
	if _ws_server and _ws_server.get_ready_state() == WebSocketPeer.STATE_OPEN:
		var text = JSON.stringify(data)
		_ws_server.send_text(text)


# ── Operations ──────────────────────────────────────────────────────

func _resolve_node(node_path: String) -> Node:
	"""Resolve um node path para o objeto Node."""
	var root = get_tree().get_edited_scene_root()
	if not root:
		return null
	if node_path == "/root" or node_path == ".":
		return root
	return root.get_node(node_path)


func _get_edited_scene_root() -> Node:
	return get_tree().get_edited_scene_root()


# ── create_node ─────────────────────────────────────────────────────

func _create_node(id, params: Dictionary) -> void:
	var parent_path: String = params.get("parent_path", "/root")
	var node_type: String = params.get("node_type", "")
	var node_name: String = params.get("node_name", "")
	var properties: Dictionary = params.get("properties", {})

	var parent = _resolve_node(parent_path)
	if not parent:
		_send_error(-32000, "Parent node not found: " + parent_path, id)
		return

	# Verifica se o tipo é válido
	if not ClassDB.class_exists(node_type):
		_send_error(-32001, "Invalid node type: " + node_type, id)
		return

	# Cria o nó
	var node: Node = ClassDB.instantiate(node_type)
	if not node:
		_send_error(-32002, "Failed to instantiate: " + node_type, id)
		return

	node.name = node_name

	# Aplica propriedades
	for prop_name in properties:
		var value = properties[prop_name]
		if prop_name in node:
			# Converte Vector2/Dictionary do JSON
			node.set(prop_name, _convert_value(value, node.get(prop_name)))

	# Registra UndoRedo
	_undo_redo.create_action("MCP: Create Node " + node_name)
	_undo_redo.add_do_method(parent, "add_child", node)
	_undo_redo.add_do_method(parent, "move_child", node, parent.get_child_count())
	_undo_redo.add_undo_method(parent, "remove_child", node)
	_undo_redo.commit_action()

	_send_result(id, {
		"status": "ok",
		"node_path": parent_path + "/" + node_name,
		"node_type": node_type,
		"instance_id": node.get_instance_id()
	})


# ── delete_node ─────────────────────────────────────────────────────

func _delete_node(id, params: Dictionary) -> void:
	var node_path: String = params.get("node_path", "")

	var node = _resolve_node(node_path)
	if not node:
		_send_error(-32000, "Node not found: " + node_path, id)
		return

	var parent = node.get_parent()
	if not parent:
		_send_error(-32003, "Cannot delete root node", id)
		return

	var idx = node.get_index()

	# UndoRedo
	_undo_redo.create_action("MCP: Delete Node " + node.name)
	_undo_redo.add_do_method(parent, "remove_child", node)
	_undo_redo.add_undo_method(parent, "add_child", node)
	_undo_redo.add_undo_method(parent, "move_child", node, idx)
	_undo_redo.commit_action()

	_send_result(id, {
		"status": "ok",
		"deleted_path": node_path
	})


# ── set_node_property ───────────────────────────────────────────────

func _set_node_property(id, params: Dictionary) -> void:
	var node_path: String = params.get("node_path", "")
	var property_name: String = params.get("property_name", "")
	var value = params.get("value", null)

	var node = _resolve_node(node_path)
	if not node:
		_send_error(-32000, "Node not found: " + node_path, id)
		return

	if not property_name in node:
		_send_error(-32004, "Property not found: " + property_name, id)
		return

	var old_value = node.get(property_name)
	var new_value = _convert_value(value, old_value)

	# UndoRedo
	_undo_redo.create_action("MCP: Set " + property_name + " on " + node.name)
	_undo_redo.add_do_property(node, property_name, new_value)
	_undo_redo.add_undo_property(node, property_name, old_value)
	_undo_redo.commit_action()

	_send_result(id, {
		"status": "ok",
		"node_path": node_path,
		"property": property_name,
		"value": new_value
	})


# ── reparent_node ───────────────────────────────────────────────────

func _reparent_node(id, params: Dictionary) -> void:
	var node_path: String = params.get("node_path", "")
	var new_parent_path: String = params.get("new_parent_path", "")

	var node = _resolve_node(node_path)
	if not node:
		_send_error(-32000, "Node not found: " + node_path, id)
		return

	var old_parent = node.get_parent()
	var new_parent = _resolve_node(new_parent_path)
	if not new_parent:
		_send_error(-32000, "New parent not found: " + new_parent_path, id)
		return

	var old_idx = node.get_index()

	# UndoRedo
	_undo_redo.create_action("MCP: Reparent " + node.name)
	_undo_redo.add_do_method(old_parent, "remove_child", node)
	_undo_redo.add_do_method(new_parent, "add_child", node)
	_undo_redo.add_undo_method(new_parent, "remove_child", node)
	_undo_redo.add_undo_method(old_parent, "add_child", node)
	_undo_redo.add_undo_method(old_parent, "move_child", node, old_idx)
	_undo_redo.commit_action()

	_send_result(id, {
		"status": "ok",
		"node_path": new_parent_path + "/" + node.name,
		"old_parent": old_parent.get_path(),
		"new_parent": new_parent.get_path()
	})


# ── duplicate_node ──────────────────────────────────────────────────

func _duplicate_node(id, params: Dictionary) -> void:
	var node_path: String = params.get("node_path", "")
	var new_name: String = params.get("new_name", "")

	var node = _resolve_node(node_path)
	if not node:
		_send_error(-32000, "Node not found: " + node_path, id)
		return

	var parent = node.get_parent()
	var duplicate = node.duplicate()
	if new_name:
		duplicate.name = new_name
	else:
		duplicate.name = node.name + "_copy"

	# UndoRedo
	_undo_redo.create_action("MCP: Duplicate " + node.name)
	_undo_redo.add_do_method(parent, "add_child", duplicate)
	_undo_redo.add_undo_method(parent, "remove_child", duplicate)
	_undo_redo.commit_action()

	_send_result(id, {
		"status": "ok",
		"node_path": parent.get_path() + "/" + duplicate.name,
		"node_type": duplicate.get_class()
	})


# ── batch_edit ──────────────────────────────────────────────────────

func _batch_edit(id, params: Dictionary) -> void:
	var operations: Array = params.get("operations", [])

	_undo_redo.create_action("MCP: Batch Edit (" + str(operations.size()) + " ops)")

	for op in operations:
		var method = op.get("method", "")
		var op_params = op.get("params", {})

		match method:
			"create_node":
				_batch_create(op_params)
			"delete_node":
				_batch_delete(op_params)
			"set_node_property":
				_batch_set_property(op_params)
			"reparent_node":
				_batch_reparent(op_params)

	_undo_redo.commit_action()

	_send_result(id, {
		"status": "ok",
		"operations": operations.size()
	})


# ── take_screenshot ─────────────────────────────────────────────────

func _take_screenshot(id, _params: Dictionary) -> void:
	var viewport = get_tree().get_root()
	if not viewport:
		_send_error(-32005, "Viewport not found", id)
		return

	var image = viewport.get_texture().get_image()
	if not image:
		_send_error(-32006, "Failed to capture screenshot", id)
		return

	# Salva no cache do MCP
	var path = "user://mcp_screenshot_" + str(Time.get_unix_time_from_system()) + ".png"
	image.save_png(path)

	_send_result(id, {
		"status": "ok",
		"path": ProjectSettings.globalize_path(path),
		"size": Vector2(image.get_width(), image.get_height())
	})


# ── get_scene_tree ──────────────────────────────────────────────────

func _get_scene_tree(id, _params: Dictionary) -> void:
	var root = _get_edited_scene_root()
	if not root:
		_send_result(id, {
			"status": "ok",
			"scene": "",
			"nodes": [],
			"message": "Nenhuma cena aberta no editor."
		})
		return

	var tree = _serialize_node(root)
	_send_result(id, {
		"status": "ok",
		"scene": root.scene_file_path if root.scene_file_path else "",
		"nodes": tree
	})


# ── Batch helpers ───────────────────────────────────────────────────

func _batch_create(params: Dictionary) -> void:
	var parent = _resolve_node(params.get("parent_path", "/root"))
	if not parent:
		return
	var node = ClassDB.instantiate(params.get("node_type", "Node"))
	if not node:
		return
	node.name = params.get("node_name", "NewNode")
	_undo_redo.add_do_method(parent, "add_child", node)
	_undo_redo.add_undo_method(parent, "remove_child", node)


func _batch_delete(params: Dictionary) -> void:
	var node = _resolve_node(params.get("node_path", ""))
	if not node or not node.get_parent():
		return
	var parent = node.get_parent()
	_undo_redo.add_do_method(parent, "remove_child", node)
	_undo_redo.add_undo_method(parent, "add_child", node)


func _batch_set_property(params: Dictionary) -> void:
	var node = _resolve_node(params.get("node_path", ""))
	if not node:
		return
	var prop = params.get("property_name", "")
	if not prop in node:
		return
	var old = node.get(prop)
	var new_val = _convert_value(params.get("value"), old)
	_undo_redo.add_do_property(node, prop, new_val)
	_undo_redo.add_undo_property(node, prop, old)


func _batch_reparent(params: Dictionary) -> void:
	var node = _resolve_node(params.get("node_path", ""))
	var new_parent = _resolve_node(params.get("new_parent_path", ""))
	if not node or not new_parent:
		return
	var old_parent = node.get_parent()
	_undo_redo.add_do_method(old_parent, "remove_child", node)
	_undo_redo.add_do_method(new_parent, "add_child", node)
	_undo_redo.add_undo_method(new_parent, "remove_child", node)
	_undo_redo.add_undo_method(old_parent, "add_child", node)


# ── Helpers ─────────────────────────────────────────────────────────

func _serialize_node(node: Node, depth: int = 0) -> Dictionary:
	var data = {
		"name": node.name,
		"type": node.get_class(),
		"path": node.get_path(),
		"depth": depth,
		"children": []
	}
	for child in node.get_children():
		data["children"].append(_serialize_node(child, depth + 1))
	return data


func _convert_value(value, template):
	"""Converte valores JSON para tipos Godot."""
	if template is Vector2 or template is Vector2i:
		if value is Dictionary:
			return Vector2(value.get("x", 0), value.get("y", 0))
	elif template is Vector3:
		if value is Dictionary:
			return Vector3(
				value.get("x", 0),
				value.get("y", 0),
				value.get("z", 0)
			)
	elif template is Color:
		if value is String:
			return Color(value)
		elif value is Dictionary:
			return Color(
				value.get("r", 1),
				value.get("g", 1),
				value.get("b", 1),
				value.get("a", 1)
			)
	return value


func _has_method(obj, method: String) -> bool:
	return obj.has_method(method)
