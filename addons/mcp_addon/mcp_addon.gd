# mcp_addon.gd — MCP Godot Agent v3.2 | Dock Profissional
#
# EditorPlugin com dock visual e WebSocket bridge para o servidor Python.
# Porta: 9082 | Protocolo: JSON-RPC 2.0 sobre WebSocket

@tool
extends EditorPlugin

const PORT = 9082
const VERSION = "3.2.0"

var _server: TCPServer
var _peer: StreamPeerTCP = null
var _ws_server: WebSocketPeer
var _connected: bool = false
var _undo_redo: EditorUndoRedoManager

# Dock UI
var _dock: Control
var _status_label: Label
var _conn_indicator: ColorRect
var _log_rich: RichTextLabel
var _stats_label: Label
var _tool_list: ItemList
var _op_count: int = 0
var _log_lines: Array[String] = []


func _enter_tree() -> void:
	_undo_redo = get_undo_redo()
	_start_server()
	_create_dock()
	print("[MCP Addon] v", VERSION, " - Dock iniciado na porta ", PORT)

func _exit_tree() -> void:
	_stop_server()
	if _dock:
		remove_control_from_bottom_panel(_dock)
		_dock.queue_free()
	print("[MCP Addon] Encerrado")

func _process(_delta: float) -> void:
	if not _server:
		return
	if not _peer and _server.is_connection_available():
		_peer = _server.take_connection()
		_ws_server = WebSocketPeer.new()
		_ws_server.accept_stream(_peer)
		_connected = true
		_update_status("Conectado", Color.GREEN)
		_add_log("[color=green]CLIENTE CONECTADO[/color]")
	if _ws_server and _ws_server.get_available_packet_count() > 0:
		var packet = _ws_server.get_packet()
		var message = packet.get_string_from_utf8()
		_handle_message(message)
	if _ws_server and _ws_server.get_ready_state() == WebSocketPeer.STATE_CLOSED:
		_peer = null; _ws_server = null; _connected = false
		_update_status("Aguardando", Color.ORANGE)
		_add_log("[color=orange]CLIENTE DESCONECTADO[/color]")


func _create_dock() -> void:
	_dock = MarginContainer.new()
	_dock.name = "MCP Agent"
	_dock.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_dock.size_flags_vertical = Control.SIZE_EXPAND_FILL

	var main_vbox = VBoxContainer.new()
	main_vbox.name = "MainVBox"
	_dock.add_child(main_vbox)

	# HEADER
	var header = PanelContainer.new()
	header.name = "Header"
	var hs = StyleBoxFlat.new()
	hs.bg_color = Color(0.08, 0.1, 0.16, 1)
	hs.content_margin_left = 10; hs.content_margin_right = 10
	hs.content_margin_top = 6; hs.content_margin_bottom = 6
	header.add_theme_stylebox_override("panel", hs)
	main_vbox.add_child(header)

	var hh = HBoxContainer.new(); header.add_child(hh)

	var title = Label.new()
	title.text = "MCP Agent"
	title.add_theme_font_size_override("font_size", 16)
	title.add_theme_color_override("font_color", Color(0.2, 0.8, 1.0))
	hh.add_child(title)

	var sp = Control.new(); sp.size_flags_horizontal = Control.SIZE_EXPAND_FILL; hh.add_child(sp)

	var ver = Label.new()
	ver.text = "v" + VERSION
	ver.add_theme_font_size_override("font_size", 10)
	ver.add_theme_color_override("font_color", Color(0.4, 0.5, 0.6))
	hh.add_child(ver)

	var vs = VSeparator.new(); vs.custom_minimum_size = Vector2(4, 4); hh.add_child(vs)

	_conn_indicator = ColorRect.new()
	_conn_indicator.custom_minimum_size = Vector2(10, 10)
	_conn_indicator.color = Color.ORANGE
	hh.add_child(_conn_indicator)

	_status_label = Label.new()
	_status_label.text = "Aguardando"
	_status_label.add_theme_font_size_override("font_size", 12)
	_status_label.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
	hh.add_child(_status_label)

	# TABS
	var tabs = TabContainer.new()
	tabs.name = "Tabs"
	tabs.size_flags_vertical = Control.SIZE_EXPAND_FILL
	main_vbox.add_child(tabs)

	# TAB 1: STATUS
	var stab = VBoxContainer.new(); stab.name = "Status"; tabs.add_child(stab)
	var grid = GridContainer.new(); grid.columns = 2
	grid.add_theme_constant_override("h_separation", 16)
	grid.add_theme_constant_override("v_separation", 6)
	var gm = MarginContainer.new()
	gm.add_theme_constant_override("margin_left", 12)
	gm.add_theme_constant_override("margin_top", 10)
	gm.add_child(grid); stab.add_child(gm)

	_add_row(grid, "Porta", str(PORT))
	_add_row(grid, "Protocolo", "JSON-RPC 2.0 / WS")
	_add_row(grid, "UndoRedo", "Nativo Godot")
	_add_row(grid, "Projeto", ProjectSettings.get_setting("application/config/name"))

	var sep2 = HSeparator.new(); stab.add_child(sep2)

	_stats_label = Label.new()
	_stats_label.text = "Operacoes: 0  |  Pronto para receber comandos"
	_stats_label.add_theme_font_size_override("font_size", 12)
	_stats_label.add_theme_color_override("font_color", Color(0.55, 0.6, 0.65))
	var sm = MarginContainer.new()
	sm.add_theme_constant_override("margin_left", 12)
	sm.add_theme_constant_override("margin_top", 8)
	sm.add_child(_stats_label); stab.add_child(sm)

	# TAB 2: LOG
	var ltab = VBoxContainer.new(); ltab.name = "Log"; tabs.add_child(ltab)
	var lh = HBoxContainer.new()
	var lt = Label.new(); lt.text = " Operacoes em Tempo Real"
	lt.add_theme_font_size_override("font_size", 12)
	lh.add_child(lt)
	var lsp = Control.new(); lsp.size_flags_horizontal = Control.SIZE_EXPAND_FILL; lh.add_child(lsp)
	var cb = Button.new(); cb.text = "Limpar"; cb.flat = true
	cb.pressed.connect(func(): _log_rich.clear(); _log_lines.clear())
	lh.add_child(cb)
	var lhm = MarginContainer.new()
	lhm.add_theme_constant_override("margin_left", 8)
	lhm.add_theme_constant_override("margin_top", 4)
	lhm.add_child(lh); ltab.add_child(lhm)

	_log_rich = RichTextLabel.new()
	_log_rich.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_log_rich.bbcode_enabled = true
	_log_rich.scroll_following = true
	_log_rich.selection_enabled = true
	var lrm = MarginContainer.new()
	lrm.add_theme_constant_override("margin_left", 8)
	lrm.add_theme_constant_override("margin_right", 8)
	lrm.add_theme_constant_override("margin_bottom", 4)
	lrm.add_child(_log_rich); ltab.add_child(lrm)

	# TAB 3: TOOLS
	var ttab = VBoxContainer.new(); ttab.name = "Tools"; tabs.add_child(ttab)
	var tlab = Label.new()
	tlab.text = " Operacoes JSON-RPC disponiveis:"
	tlab.add_theme_font_size_override("font_size", 12)
	var tlm = MarginContainer.new()
	tlm.add_theme_constant_override("margin_left", 12)
	tlm.add_theme_constant_override("margin_top", 8)
	tlm.add_child(tlab); ttab.add_child(tlm)

	_tool_list = ItemList.new()
	_tool_list.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var tools_data = [
		"ping              - Verificar conexao",
		"create_node       - Criar no na cena (UndoRedo)",
		"delete_node       - Remover no da cena (UndoRedo)",
		"set_node_property - Alterar propriedade (UndoRedo)",
		"reparent_node     - Mover no na arvore (UndoRedo)",
		"duplicate_node    - Duplicar no (UndoRedo)",
		"batch_edit        - Edicao em lote atomica",
		"take_screenshot   - Capturar tela do editor",
		"get_scene_tree    - Arvore completa da cena",
	]
	for td in tools_data: _tool_list.add_item("  " + td)
	var tlm2 = MarginContainer.new()
	tlm2.add_theme_constant_override("margin_left", 8)
	tlm2.add_theme_constant_override("margin_right", 8)
	tlm2.add_child(_tool_list); ttab.add_child(tlm2)

	# FOOTER
	var footer = Label.new()
	footer.text = "github.com/joabcostamd/mcp-godot-desenvolvimento"
	footer.add_theme_font_size_override("font_size", 9)
	footer.add_theme_color_override("font_color", Color(0.3, 0.3, 0.4))
	footer.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var fm = MarginContainer.new()
	fm.add_theme_constant_override("margin_bottom", 3)
	fm.add_child(footer); main_vbox.add_child(fm)

	add_control_to_bottom_panel(_dock, "MCP Agent")
	_add_log("MCP Agent v" + VERSION + " iniciado na porta " + str(PORT))

func _add_row(grid: GridContainer, label: String, value: String) -> void:
	var l = Label.new(); l.text = label
	l.add_theme_color_override("font_color", Color(0.45, 0.55, 0.65))
	grid.add_child(l)
	var v = Label.new(); v.text = value
	v.add_theme_color_override("font_color", Color(0.8, 0.85, 0.9))
	grid.add_child(v)

func _update_status(text: String, color: Color) -> void:
	_status_label.text = text
	_conn_indicator.color = color

func _add_log(msg: String) -> void:
	var ts = Time.get_time_string_from_system()
	_log_lines.append("[" + ts + "] " + msg)
	if _log_lines.size() > 200:
		_log_lines.pop_front()
	if _log_rich:
		_log_rich.clear()
		for line in _log_lines:
			_log_rich.append_text(line + "\n")

func _update_stats(op: String, ok: bool) -> void:
	_op_count += 1
	_stats_label.text = "Operacoes: " + str(_op_count) + "  |  Ultima: " + op + ("  OK" if ok else "  ERRO")


func _start_server() -> void:
	_server = TCPServer.new()
	if _server.listen(PORT) != OK:
		push_error("[MCP Addon] Falha ao iniciar servidor na porta ", PORT)
		_server = null
		_add_log("[color=red]ERRO: Falha ao iniciar servidor[/color]")

func _stop_server() -> void:
	if _peer: _peer = null
	if _server: _server.stop(); _server = null
	_connected = false


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

	_add_log("[color=cyan]" + method + "[/color]")
	_update_stats(method, true)

	match method:
		"ping": _send_result(req_id, {"status": "ok", "message": "pong"})
		"create_node": _create_node(req_id, params)
		"delete_node": _delete_node(req_id, params)
		"set_node_property": _set_node_property(req_id, params)
		"reparent_node": _reparent_node(req_id, params)
		"duplicate_node": _duplicate_node(req_id, params)
		"batch_edit": _batch_edit(req_id, params)
		"take_screenshot": _take_screenshot(req_id, params)
		"get_scene_tree": _get_scene_tree(req_id, params)
		_:
			_send_error(-32601, "Method not found: " + method, req_id)
			_update_stats(method, false)


func _send_result(id, result: Dictionary) -> void:
	_send({"jsonrpc": "2.0", "id": id, "result": result})

func _send_error(code: int, message: String, id = null) -> void:
	_send({"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}})

func _send(data: Dictionary) -> void:
	if _ws_server and _ws_server.get_ready_state() == WebSocketPeer.STATE_OPEN:
		_ws_server.send_text(JSON.stringify(data))


func _resolve_node(path: String) -> Node:
	var root = get_tree().get_edited_scene_root()
	if not root: return null
	if path == "/root" or path == ".": return root
	return root.get_node(path)

func _convert_value(value, old_value):
	if value is Dictionary:
		if value.has("x") and value.has("y"):
			return Vector2(float(value.x), float(value.y))
		if value.has("r") and value.has("g") and value.has("b"):
			return Color(value.r, value.g, value.b, value.get("a", 1.0))
	if old_value is Vector2 and value is String:
		var p = value.split(",", false)
		if p.size() == 2: return Vector2(float(p[0]), float(p[1]))
	if old_value is int and value is String: return int(value)
	if old_value is float and value is String: return float(value)
	if old_value is bool and value is String: return value.to_lower() == "true"
	return value


func _create_node(id, params: Dictionary) -> void:
	var pp = params.get("parent_path", "/root")
	var nt = params.get("node_type", "")
	var nn = params.get("node_name", "")
	var pr = params.get("properties", {})
	var parent = _resolve_node(pp)
	if not parent: _send_error(-32000, "Parent not found", id); return
	if not ClassDB.class_exists(nt): _send_error(-32001, "Invalid type: " + nt, id); return
	var node: Node = ClassDB.instantiate(nt)
	if not node: _send_error(-32002, "Failed to instantiate", id); return
	node.name = nn
	for pn in pr:
		if pn in node: node.set(pn, _convert_value(pr[pn], node.get(pn)))
	_undo_redo.create_action("MCP: Create " + nn)
	_undo_redo.add_do_method(parent, "add_child", node)
	_undo_redo.add_undo_method(parent, "remove_child", node)
	_undo_redo.commit_action()
	_send_result(id, {"status": "ok", "node_path": pp + "/" + nn})
	_add_log("  Criado: " + nn + " (" + nt + ")")

func _delete_node(id, params: Dictionary) -> void:
	var np = params.get("node_path", "")
	var node = _resolve_node(np)
	if not node: _send_error(-32000, "Node not found", id); return
	var parent = node.get_parent()
	if not parent: _send_error(-32003, "Cannot delete root", id); return
	var idx = node.get_index()
	_undo_redo.create_action("MCP: Delete " + node.name)
	_undo_redo.add_do_method(parent, "remove_child", node)
	_undo_redo.add_undo_method(parent, "add_child", node)
	_undo_redo.add_undo_method(parent, "move_child", node, idx)
	_undo_redo.commit_action()
	_send_result(id, {"status": "ok"})

func _set_node_property(id, params: Dictionary) -> void:
	var np = params.get("node_path", "")
	var pn = params.get("property_name", "")
	var pv = params.get("value", null)
	var node = _resolve_node(np)
	if not node: _send_error(-32000, "Node not found", id); return
	if not pn in node: _send_error(-32004, "Property not found: " + pn, id); return
	var ov = node.get(pn)
	var nv = _convert_value(pv, ov)
	_undo_redo.create_action("MCP: Set " + pn)
	_undo_redo.add_do_property(node, pn, nv)
	_undo_redo.add_undo_property(node, pn, ov)
	_undo_redo.commit_action()
	_send_result(id, {"status": "ok"})

func _reparent_node(id, params: Dictionary) -> void:
	var np = params.get("node_path", "")
	var npp = params.get("new_parent_path", "")
	var node = _resolve_node(np)
	var new_parent = _resolve_node(npp)
	if not node or not new_parent: _send_error(-32000, "Node not found", id); return
	var old_parent = node.get_parent()
	var idx = node.get_index()
	_undo_redo.create_action("MCP: Reparent " + node.name)
	_undo_redo.add_do_method(old_parent, "remove_child", node)
	_undo_redo.add_do_method(new_parent, "add_child", node)
	_undo_redo.add_undo_method(new_parent, "remove_child", node)
	_undo_redo.add_undo_method(old_parent, "add_child", node)
	_undo_redo.add_undo_method(old_parent, "move_child", node, idx)
	_undo_redo.commit_action()
	_send_result(id, {"status": "ok"})

func _duplicate_node(id, params: Dictionary) -> void:
	var np = params.get("node_path", "")
	var nn = params.get("new_name", "")
	var node = _resolve_node(np)
	if not node: _send_error(-32000, "Node not found", id); return
	var parent = node.get_parent()
	var dup = node.duplicate()
	dup.name = nn if nn else node.name + "_copy"
	_undo_redo.create_action("MCP: Duplicate " + node.name)
	_undo_redo.add_do_method(parent, "add_child", dup)
	_undo_redo.add_undo_method(parent, "remove_child", dup)
	_undo_redo.commit_action()
	_send_result(id, {"status": "ok", "node_path": str(parent.get_path()) + "/" + dup.name})

func _batch_edit(id, params: Dictionary) -> void:
	var ops: Array = params.get("operations", [])
	_undo_redo.create_action("MCP: Batch (" + str(ops.size()) + " ops)")
	for op in ops:
		var ot = op.get("op", "")
		var opath = op.get("node_path", "")
		var node = _resolve_node(opath)
		if not node: continue
		match ot:
			"set_property":
				var pn2 = op.get("property_name", "")
				var pv2 = op.get("value", null)
				if pn2 in node:
					var ov2 = node.get(pn2)
					_undo_redo.add_do_property(node, pn2, _convert_value(pv2, ov2))
					_undo_redo.add_undo_property(node, pn2, ov2)
			"delete":
				var p = node.get_parent()
				if p:
					var idx2 = node.get_index()
					_undo_redo.add_do_method(p, "remove_child", node)
					_undo_redo.add_undo_method(p, "add_child", node)
					_undo_redo.add_undo_method(p, "move_child", node, idx2)
	_undo_redo.commit_action()
	_send_result(id, {"status": "ok", "count": ops.size()})

func _take_screenshot(id, params: Dictionary) -> void:
	var ei = get_editor_interface()
	var bc = ei.get_base_control()
	if not bc: _send_error(-32000, "Editor nao disponivel", id); return
	var img = bc.get_viewport().get_texture().get_image()
	if not img: _send_error(-32001, "Falha ao capturar", id); return
	var path = params.get("save_path", "res://screenshot.png")
	img.save_png(path)
	_send_result(id, {"status": "ok", "path": path})
	_add_log("  Screenshot: " + path)

func _get_scene_tree(id, _params: Dictionary) -> void:
	var root = get_tree().get_edited_scene_root()
	if not root:
		_send_result(id, {"status": "ok", "tree": [], "message": "Nenhuma cena aberta"})
		return
	_send_result(id, {"status": "ok", "tree": _build_tree(root)})

func _build_tree(node: Node) -> Dictionary:
	var r = {"name": node.name, "type": node.get_class(), "children": []}
	for c in node.get_children():
		r.children.append(_build_tree(c))
	return r
