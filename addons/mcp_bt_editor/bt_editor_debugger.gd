## bt_editor_debugger.gd — MCP BT Editor | Debug ao vivo via WebSocket 9082.
##
## Conecta ao jogo rodando via WebSocket (mesma porta do mcp_dock).
## Features:
##   - Breakpoints visuais: clique direito no no → "Toggle Breakpoint"
##   - Destaque de nos ativos (set_connection_activity)
##   - Watch Window: valores de variaveis em tempo real
##   - Play/Pause/Continue via botoes
##   - Integracao com EngineDebugger (100% GDScript nativo)
##
## @tutorial: https://docs.godotengine.org/en/stable/classes/class_enginedebugger.html

@tool
extends VBoxContainer

# ── Sinais ────────────────────────────────────────────────────────────────────

signal debug_paused(node_name: String)
signal debug_continued()
signal variable_updated(node_name: String, variables: Dictionary)

# ── Constantes ────────────────────────────────────────────────────────────────

const WS_PORT: int = 9082
const WS_URL: String = "ws://127.0.0.1:%d" % WS_PORT
const RECONNECT_INTERVAL: float = 3.0

# ── Estado ────────────────────────────────────────────────────────────────────

var _ws: WebSocketPeer = null
var _connected: bool = false
var _reconnect_timer: float = 0.0
var _graph_edit: GraphEdit = null
var _breakpoints: Dictionary = {}        # node_name -> bool
var _active_node: String = ""
var _is_paused: bool = false
var _watch_data: Dictionary = {}

# ── Referencias UI ────────────────────────────────────────────────────────────

var _status_label: Label
var _watch_tree: Tree
var _btn_play: Button
var _btn_pause: Button
var _btn_step: Button
var _btn_continue: Button


# ── Ciclo de vida ─────────────────────────────────────────────────────────────

func _ready() -> void:
	_build_ui()
	_setup_websocket()


func _process(delta: float) -> void:
	if _ws:
		_ws.poll()
		_process_ws_messages()

	if not _connected:
		_reconnect_timer -= delta
		if _reconnect_timer <= 0.0:
			_setup_websocket()


func _exit_tree() -> void:
	if _ws:
		_ws.close()
		_ws = null


# ── UI ────────────────────────────────────────────────────────────────────────

func _build_ui() -> void:
	# Header
	var header: Label = Label.new()
	header.name = "DebuggerHeader"
	header.text = "🐛 Debugger"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 13)
	add_child(header)

	# Status
	_status_label = Label.new()
	_status_label.name = "DebugStatus"
	_status_label.text = "⏳ Desconectado"
	_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_status_label.add_theme_color_override("font_color", Color(0.9, 0.5, 0.1))
	add_child(_status_label)

	# Botoes de controle
	var btn_row: HBoxContainer = HBoxContainer.new()
	btn_row.name = "DebugButtons"
	btn_row.alignment = BoxContainer.ALIGNMENT_CENTER

	_btn_play = Button.new()
	_btn_play.text = "▶"
	_btn_play.tooltip_text = "Iniciar execucao"
	_btn_play.pressed.connect(_on_play_pressed)
	btn_row.add_child(_btn_play)

	_btn_pause = Button.new()
	_btn_pause.text = "⏸"
	_btn_pause.tooltip_text = "Pausar execucao"
	_btn_pause.disabled = true
	_btn_pause.pressed.connect(_on_pause_pressed)
	btn_row.add_child(_btn_pause)

	_btn_step = Button.new()
	_btn_step.text = "⏭"
	_btn_step.tooltip_text = "Passo a passo"
	_btn_step.disabled = true
	_btn_step.pressed.connect(_on_step_pressed)
	btn_row.add_child(_btn_step)

	_btn_continue = Button.new()
	_btn_continue.text = "▶▶"
	_btn_continue.tooltip_text = "Continuar"
	_btn_continue.disabled = true
	_btn_continue.pressed.connect(_on_continue_pressed)
	btn_row.add_child(_btn_continue)

	add_child(btn_row)

	# Separador
	var sep: HSeparator = HSeparator.new()
	add_child(sep)

	# Watch Window
	var watch_header: Label = Label.new()
	watch_header.text = "📊 Watch"
	watch_header.add_theme_font_size_override("font_size", 11)
	add_child(watch_header)

	_watch_tree = Tree.new()
	_watch_tree.name = "WatchTree"
	_watch_tree.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_watch_tree.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_watch_tree.hide_root = true
	_watch_tree.columns = 2
	_watch_tree.set_column_title(0, "Variavel")
	_watch_tree.set_column_title(1, "Valor")
	_watch_tree.set_column_expand(0, true)
	_watch_tree.set_column_expand(1, true)
	add_child(_watch_tree)

	# Placeholder
	var root: TreeItem = _watch_tree.create_item()
	var item: TreeItem = _watch_tree.create_item(root)
	item.set_text(0, "(aguardando execucao)")
	item.set_selectable(0, false)
	item.set_selectable(1, false)


# ── API Publica ───────────────────────────────────────────────────────────────

func set_graph_edit(graph: GraphEdit) -> void:
	_graph_edit = graph


func toggle_breakpoint(node: GraphNode) -> void:
	"""Alterna breakpoint no no especificado."""
	if not node:
		return
	var node_name: String = node.name
	var has_bp: bool = _breakpoints.get(node_name, false)

	if has_bp:
		# Remover breakpoint visual
		_breakpoints.erase(node_name)
		_remove_visual_breakpoint(node)
	else:
		# Adicionar breakpoint
		_breakpoints[node_name] = true
		_add_visual_breakpoint(node)


func is_paused() -> bool:
	return _is_paused


func get_active_node() -> String:
	return _active_node


func get_watch_data() -> Dictionary:
	return _watch_data.duplicate()


# ── WebSocket ─────────────────────────────────────────────────────────────────

func _setup_websocket() -> void:
	if _ws:
		_ws.close()
		_ws = null
	_ws = WebSocketPeer.new()
	var err: int = _ws.connect_to_url(WS_URL)
	if err != OK:
		_update_status("⏳ Conectando... (%d)" % err, Color(0.9, 0.5, 0.1))
		_reconnect_timer = RECONNECT_INTERVAL
	else:
		_update_status("⏳ Conectando...", Color(0.9, 0.5, 0.1))


func _process_ws_messages() -> void:
	while _ws.get_available_packet_count() > 0:
		var packet: PackedByteArray = _ws.get_packet()
		var text: String = packet.get_string_from_utf8()

		if _ws.was_string_packet():
			_handle_message(text)


func _handle_message(text: String) -> void:
	# Tenta parse JSON-RPC
	var json: JSON = JSON.new()
	var err: int = json.parse(text)
	if err != OK:
		return
	var data: Variant = json.get_data()
	if typeof(data) != TYPE_DICTIONARY:
		return

	var msg: Dictionary = data
	var msg_type: String = msg.get("type", "")

	match msg_type:
		"connected":
			_connected = true
			_update_status("✅ Conectado (porta %d)" % WS_PORT, Color(0.3, 0.9, 0.3))
		"disconnected":
			_connected = false
			_update_status("⏳ Desconectado", Color(0.9, 0.5, 0.1))
		"breakpoint_hit":
			_on_breakpoint_hit(msg)
		"variable_update":
			_on_variable_update(msg)
		"node_active":
			_on_node_active(msg)
		"execution_finished":
			_on_execution_finished()
		_:
			pass


func _send_message(msg: Dictionary) -> void:
	if not _ws or _ws.get_ready_state() != WebSocketPeer.STATE_OPEN:
		return
	var json: JSON = JSON.new()
	var text: String = json.stringify(msg)
	_ws.send_text(text)


# ── Breakpoint Handling ───────────────────────────────────────────────────────

func _on_breakpoint_hit(msg: Dictionary) -> void:
	"""Recebido quando um breakpoint e atingido no jogo."""
	var node_name: String = msg.get("node", "")
	_is_paused = true
	_active_node = node_name

	_update_status("⏸ Pausado em: %s" % node_name, Color(0.3, 0.5, 0.95))
	_update_debug_buttons(true)

	# Destacar no ativo no grafo
	if _graph_edit:
		_highlight_node(node_name, true)

	debug_paused.emit(node_name)

	# Solicitar valores das variaveis
	_send_message({
		"type": "get_variables",
		"node": node_name,
	})


func _on_variable_update(msg: Dictionary) -> void:
	"""Recebe valores das variaveis do jogo."""
	var node_name: String = msg.get("node", "")
	var variables: Dictionary = msg.get("variables", {})
	_watch_data = variables
	_populate_watch(variables)
	variable_updated.emit(node_name, variables)


func _on_node_active(msg: Dictionary) -> void:
	"""Recebe notificacao de no ativo durante execucao."""
	var node_name: String = msg.get("node", "")
	_active_node = node_name

	if _graph_edit:
		_highlight_node(node_name, true)

	# Auto-limpa highlight apos 500ms
	var timer: SceneTreeTimer = get_tree().create_timer(0.5)
	timer.timeout.connect(func():
		if _graph_edit and not _is_paused:
			_highlight_node(node_name, false)
	)


func _on_execution_finished() -> void:
	_is_paused = false
	_active_node = ""
	_update_status("✅ Execucao concluida", Color(0.3, 0.9, 0.3))
	_update_debug_buttons(false)
	_clear_all_highlights()


# ── Controles ─────────────────────────────────────────────────────────────────

func _on_play_pressed() -> void:
	_send_message({"type": "play"})
	_update_status("▶ Executando...", Color(0.3, 0.9, 0.3))
	_is_paused = false
	_update_debug_buttons(false)
	_clear_all_highlights()


func _on_pause_pressed() -> void:
	_send_message({"type": "pause"})
	_update_status("⏸ Pausando...", Color(0.9, 0.5, 0.1))


func _on_step_pressed() -> void:
	_send_message({"type": "step"})
	_update_status("⏭ Passo...", Color(0.3, 0.5, 0.95))


func _on_continue_pressed() -> void:
	_send_message({"type": "continue"})
	_is_paused = false
	_update_status("▶▶ Continuando...", Color(0.3, 0.9, 0.3))
	_update_debug_buttons(false)
	_clear_all_highlights()
	debug_continued.emit()


# ── Visual ────────────────────────────────────────────────────────────────────

func _add_visual_breakpoint(node: GraphNode) -> void:
	"""Marca visual de breakpoint (borda vermelha)."""
	var sb: StyleBoxFlat = StyleBoxFlat.new()
	sb.bg_color = Color(0.9, 0.1, 0.1, 0.15)
	sb.border_color = Color(0.9, 0.1, 0.1)
	sb.border_width_left = 3
	sb.border_width_right = 3
	sb.border_width_top = 3
	sb.border_width_bottom = 3
	node.add_theme_stylebox_override("panel", sb)


func _remove_visual_breakpoint(node: GraphNode) -> void:
	"""Remove marca visual de breakpoint."""
	node.remove_theme_stylebox_override("panel")


func _highlight_node(node_name: String, active: bool) -> void:
	if not _graph_edit:
		return
	var n: Node = _graph_edit.get_node_or_null(node_name)
	if not n or not n is GraphNode:
		return
	var gn: GraphNode = n as GraphNode

	if active:
		var sb: StyleBoxFlat = StyleBoxFlat.new()
		sb.bg_color = Color(0.1, 0.9, 0.1, 0.2)
		sb.border_color = Color(0.1, 0.8, 0.1)
		sb.border_width_left = 2
		sb.border_width_right = 2
		sb.border_width_top = 2
		sb.border_width_bottom = 2
		gn.add_theme_stylebox_override("panel", sb)
	else:
		# Restaurar (remove override)
		gn.remove_theme_stylebox_override("panel")
		# Re-aplicar breakpoint se existir
		if _breakpoints.get(node_name, false):
			_add_visual_breakpoint(gn)


func _clear_all_highlights() -> void:
	if not _graph_edit:
		return
	for child: Node in _graph_edit.get_children():
		if child is GraphNode:
			var gn: GraphNode = child as GraphNode
			gn.remove_theme_stylebox_override("panel")
			if _breakpoints.get(child.name, false):
				_add_visual_breakpoint(gn)


# ── Watch Window ──────────────────────────────────────────────────────────────

func _populate_watch(variables: Dictionary) -> void:
	_watch_tree.clear()
	var root: TreeItem = _watch_tree.create_item()

	if variables.is_empty():
		var empty_item: TreeItem = _watch_tree.create_item(root)
		empty_item.set_text(0, "(sem variaveis)")
		return

	var keys: Array = variables.keys()
	keys.sort()
	for key in keys:
		var value: Variant = variables[key]
		var watch_item: TreeItem = _watch_tree.create_item(root)
		watch_item.set_text(0, str(key))
		watch_item.set_text(1, _format_value(value))
		watch_item.set_selectable(0, false)
		watch_item.set_selectable(1, false)

		# Cor por tipo
		match typeof(value):
			TYPE_INT, TYPE_FLOAT:
				watch_item.set_custom_color(1, Color(0.3, 0.7, 1.0))
			TYPE_STRING:
				watch_item.set_custom_color(1, Color(0.3, 0.9, 0.3))
			TYPE_BOOL:
				watch_item.set_custom_color(1, Color(0.9, 0.7, 0.1))
			_:
				watch_item.set_custom_color(1, Color(0.7, 0.7, 0.7))


func _format_value(value: Variant) -> String:
	match typeof(value):
		TYPE_NIL: return "null"
		TYPE_BOOL: return "true" if value else "false"
		TYPE_INT: return str(value)
		TYPE_FLOAT: return "%.3f" % value
		TYPE_STRING: return "\"%s\"" % str(value)
		TYPE_VECTOR2:
			var v2: Vector2 = value
			return "Vector2(%.1f, %.1f)" % [v2.x, v2.y]
		TYPE_VECTOR3:
			var v3: Vector3 = value
			return "Vector3(%.1f, %.1f, %.1f)" % [v3.x, v3.y, v3.z]
		TYPE_COLOR: return str(value)
		_: return str(value)


# ── Helpers ───────────────────────────────────────────────────────────────────

func _update_status(text: String, color: Color) -> void:
	_status_label.text = text
	_status_label.add_theme_color_override("font_color", color)


func _update_debug_buttons(paused: bool) -> void:
	_btn_play.disabled = paused
	_btn_pause.disabled = not paused
	_btn_step.disabled = not paused
	_btn_continue.disabled = not paused
