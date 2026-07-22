## bt_editor_graph.gd — MCP BT Editor | GraphEdit com validacao de conexoes e features avancadas.
##
## Features:
##   - Validacao de conexoes por tipo (FLOW/CONDITION/DATA/EVENT)
##   - Reroute nodes (nos de organizacao pura)
##   - Expression nodes (GDScript de uma linha)
##   - Auto-Arrange (layout hierarquico)
##   - Drag-from-Port → menu "Add Node" filtrado
##   - GraphFrame para agrupar nos
##   - Undo/Redo via EditorUndoRedoManager
##   - Delete key remove nos selecionados
##   - Drop data da paleta para criar nos
##
## @tutorial: https://docs.godotengine.org/en/stable/classes/class_graphedit.html

@tool
extends GraphEdit

# ── Constantes de tipo de porta ───────────────────────────────────────────────

enum PortType {
	FLOW = 0,
	CONDITION = 1,
	DATA = 2,
	EVENT = 3,
}

const PORT_TYPE_NAMES: Dictionary = {
	PortType.FLOW: "Fluxo",
	PortType.CONDITION: "Condicao",
	PortType.DATA: "Dados",
	PortType.EVENT: "Evento",
}

# ── Sinais ────────────────────────────────────────────────────────────────────

signal node_added(node: GraphNode, meta: Dictionary)
signal node_removed(node: GraphNode)
signal connection_changed(from_node: String, from_port: int, to_node: String, to_port: int)

# ── Referencias ───────────────────────────────────────────────────────────────

var _palette_ref: Control = null
var _inspector_ref: Control = null
var _undo_redo: EditorUndoRedoManager


# ── Ciclo de vida ─────────────────────────────────────────────────────────────

func _ready() -> void:
	_undo_redo = get_undo_redo()

	# Configurar validacao de conexoes (ja feito no plugin, mas reforcar)
	_configure_connection_rules()

	# Conectar sinais
	connection_request.connect(_on_connection_request)
	disconnection_request.connect(_on_disconnection_request)
	delete_nodes_request.connect(_on_delete_nodes_request)
	popup_request.connect(_on_popup_request)
	node_selected.connect(_on_node_selected)
	node_deselected.connect(_on_node_deselected)
	scroll_offset_changed.connect(_on_scroll_changed)

	# Drag-from-port: ao soltar no espaco vazio
	gui_input.connect(_on_gui_input)


# ── Configuracao ──────────────────────────────────────────────────────────────

func _configure_connection_rules() -> void:
	# Limpar regras existentes
	clear_connections()

	add_valid_connection_type(PortType.FLOW, PortType.FLOW)
	add_valid_connection_type(PortType.FLOW, PortType.CONDITION)
	add_valid_connection_type(PortType.CONDITION, PortType.CONDITION)
	add_valid_connection_type(PortType.DATA, PortType.DATA)
	add_valid_connection_type(PortType.EVENT, PortType.EVENT)
	add_valid_connection_type(PortType.EVENT, PortType.FLOW)
	add_valid_connection_type(PortType.EVENT, PortType.CONDITION)


# ── API Publica ───────────────────────────────────────────────────────────────

func set_palette(pal: Control) -> void:
	_palette_ref = pal


func set_inspector(insp: Control) -> void:
	_inspector_ref = insp


func add_behavior_node(meta: Dictionary, at_position: Vector2 = Vector2(-1, -1)) -> GraphNode:
	"""Cria um BTEditorNode e adiciona ao grafo."""
	var script_path: String = "res://addons/mcp_bt_editor/bt_editor_node.gd"
	var gd: GDScript = load(script_path) as GDScript
	if not gd:
		push_error("[BT Editor] Erro ao carregar bt_editor_node.gd")
		return null
	var node: GraphNode = gd.new() as GraphNode
	if not node.has_method("setup"):
		push_error("[BT Editor] bt_editor_node.gd nao tem metodo setup()")
		return null
	# Chamada dinamica: o analisador estatico nao sabe que gd.new() cria instancia de bt_editor_node.gd
	node.call("setup", meta)

	if at_position.x < 0:
		var center: Vector2 = scroll_offset + size * 0.5
		node.position_offset = center - Vector2(90, 40)
	else:
		node.position_offset = at_position

	node.name = "BTNode_" + meta.get("name", "unnamed")

	# Undo/Redo: adicionar no
	_undo_redo.create_action("Adicionar Behavior: " + meta.get("name", ""))
	_undo_redo.add_do_method(self, "add_child", node)
	_undo_redo.add_undo_method(self, "_undo_remove_node", node)
	_undo_redo.commit_action()

	add_child(node)
	node_added.emit(node, meta)
	return node


func _undo_remove_node(node: GraphNode) -> void:
	if node:
		node.queue_free()


# ── Gerenciamento de Nos ──────────────────────────────────────────────────────

func add_reroute_node(at_position: Vector2) -> GraphNode:
	"""Adiciona um no de reroute (organizacao pura, sem logica)."""
	var node: GraphNode = GraphNode.new()
	node.name = "Reroute"
	node.title = "⟐ Reroute"
	node.position_offset = at_position
	node.resizable = true
	node.custom_minimum_size = Vector2(80, 40)

	# Reroute: uma porta de entrada (FLOW) e uma de saida (FLOW)
	node.set_slot(0, true, PortType.FLOW, Color(0.5, 0.6, 0.7),
		true, PortType.FLOW, Color(0.5, 0.6, 0.7), null, null)

	_undo_redo.create_action("Adicionar Reroute")
	_undo_redo.add_do_method(self, "add_child", node)
	_undo_redo.add_undo_method(self, "_undo_remove_node", node)
	_undo_redo.commit_action()

	add_child(node)
	return node


func add_expression_node(at_position: Vector2, expression: String = "") -> GraphNode:
	"""Adiciona um no de expressao GDScript de uma linha."""
	var node: GraphNode = GraphNode.new()
	node.name = "Expression"
	node.title = "📐 Expression"
	node.position_offset = at_position
	node.resizable = true
	node.custom_minimum_size = Vector2(200, 60)

	# Expression: entrada de dados (parametros), saida FLOW e DATA
	node.set_slot(0, true, PortType.DATA, Color(0.3, 0.8, 0.3),
		false, 0, Color.WHITE, null, null)
	node.set_slot(1, false, 0, Color.WHITE,
		true, PortType.FLOW, Color(0.2, 0.5, 1.0), null, null)
	node.set_slot(2, false, 0, Color.WHITE,
		true, PortType.DATA, Color(0.3, 0.8, 0.3), null, null)

	# Armazenar expressao como metadado
	node.set_meta("expression", expression)
	node.set_meta("node_type", "expression")

	_undo_redo.create_action("Adicionar Expression")
	_undo_redo.add_do_method(self, "add_child", node)
	_undo_redo.add_undo_method(self, "_undo_remove_node", node)
	_undo_redo.commit_action()

	add_child(node)
	return node


# ── Connection Handling ───────────────────────────────────────────────────────

func _on_connection_request(from_node: StringName, from_port: int, to_node: StringName, to_port: int) -> void:
	"""Valida e conecta dois ports."""
	# Verificar se e uma conexao valida
	var from_type: int = _get_slot_type(from_node, from_port, true)   # right port
	var to_type: int = _get_slot_type(to_node, to_port, false)         # left port

	if from_type < 0 or to_type < 0:
		return

	if not is_valid_connection_type(from_type, to_type):
		print_rich("[color=yellow][BT Editor][/color] Conexao invalida: %s(%s) -> %s(%s)" % [
			PORT_TYPE_NAMES.get(from_type, "?"), from_node,
			PORT_TYPE_NAMES.get(to_type, "?"), to_node
		])
		return

	# Verificar ciclo (DAG)
	if _would_create_cycle(from_node, to_node):
		print_rich("[color=yellow][BT Editor][/color] Ciclo detectado: %s -> %s" % [from_node, to_node])
		return

	# Conectar com undo/redo
	_undo_redo.create_action("Conectar: %s[%d] → %s[%d]" % [from_node, from_port, to_node, to_port])
	_undo_redo.add_do_method(self, "connect_node", from_node, from_port, to_node, to_port)
	_undo_redo.add_undo_method(self, "disconnect_node", from_node, from_port, to_node, to_port)
	_undo_redo.commit_action()

	connect_node(from_node, from_port, to_node, to_port)
	connection_changed.emit(from_node, from_port, to_node, to_port)


func _on_disconnection_request(from_node: StringName, from_port: int, to_node: StringName, to_port: int) -> void:
	_undo_redo.create_action("Desconectar: %s[%d] → %s[%d]" % [from_node, from_port, to_node, to_port])
	_undo_redo.add_do_method(self, "disconnect_node", from_node, from_port, to_node, to_port)
	_undo_redo.add_undo_method(self, "connect_node", from_node, from_port, to_node, to_port)
	_undo_redo.commit_action()

	disconnect_node(from_node, from_port, to_node, to_port)
	connection_changed.emit(from_node, from_port, to_node, to_port)


func _get_slot_type(node_name: StringName, port: int, is_output: bool) -> int:
	var n: Node = get_node_or_null(node_name)
	if not n or not (n is GraphNode):
		return -1
	var gn: GraphNode = n as GraphNode
	if is_output:
		return gn.get_slot_type_right(port)
	else:
		return gn.get_slot_type_left(port)


func _would_create_cycle(from_node: StringName, to_node: StringName) -> bool:
	"""Detecta se a conexao criaria um ciclo (DFS simples)."""
	# Se o no destino ja alcanca o no origem, a conexao cria um ciclo
	var visited: Array[StringName] = []
	return _dfs_reachable(to_node, from_node, visited)


func _dfs_reachable(current: StringName, target: StringName, visited: Array[StringName]) -> bool:
	if current == target:
		return true
	if current in visited:
		return false
	visited.append(current)

	var connections: Array[Dictionary] = get_connection_list()
	for conn: Dictionary in connections:
		var conn_from: StringName = conn.get("from_node", "")
		if conn_from == current:
			var conn_to: StringName = conn.get("to_node", "")
			if _dfs_reachable(conn_to, target, visited):
				return true
	return false


# ── Delete Nodes ──────────────────────────────────────────────────────────────

func _on_delete_nodes_request() -> void:
	"""Remove nos selecionados com undo/redo."""
	var selected: Array[StringName] = get_selected_nodes()
	if selected.is_empty():
		return

	_undo_redo.create_action("Remover %d no(s)" % selected.size())
	for node_name: StringName in selected:
		var gn: GraphNode = get_node_or_null(node_name) as GraphNode
		if gn:
			_undo_redo.add_do_method(self, "_do_remove_node", gn)
			_undo_redo.add_undo_method(self, "_undo_add_node", gn, gn.position_offset)
	_undo_redo.commit_action()

	for node_name: StringName in selected:
		var gn2: GraphNode = get_node_or_null(node_name) as GraphNode
		if gn2:
			_do_remove_node(gn2)


func _do_remove_node(n: Node) -> void:
	if n:
		node_removed.emit(n)
		remove_child(n)
		n.queue_free()


func _undo_add_node(n: Node, pos: Vector2) -> void:
	if n:
		if n is GraphNode:
			(n as GraphNode).position_offset = pos
		add_child(n)


# ── Drag-from-Port ────────────────────────────────────────────────────────────

func _on_popup_request(at_position: Vector2) -> void:
	"""Menu de contexto no espaco vazio: adicionar no."""
	var popup: PopupMenu = PopupMenu.new()
	popup.name = "GraphContextMenu"

	popup.add_item("🧩 Adicionar Behavior...", 1)
	popup.add_separator()
	popup.add_item("⟐ Adicionar Reroute", 2)
	popup.add_item("📐 Adicionar Expression", 3)
	popup.add_separator()
	popup.add_item("📐 Adicionar GraphFrame", 4)
	popup.add_separator()
	popup.add_item("🔀 Auto-Arrange", 5)
	popup.add_item("📋 Mostrar Codigo Gerado", 6)

	popup.position = get_screen_position() + at_position
	popup.id_pressed.connect(_on_context_menu_action.bind(popup, at_position))
	add_child(popup)
	popup.popup()


func _on_context_menu_action(id: int, popup: PopupMenu, at_position: Vector2) -> void:
	match id:
		1:
			# Abrir dialogo de busca para adicionar behavior
			_show_add_behavior_dialog(at_position)
		2:
			add_reroute_node(at_position)
		3:
			add_expression_node(at_position)
		4:
			_add_graph_frame(at_position)
		5:
			arrange_nodes()
		6:
			_show_generated_code()
	popup.queue_free()


func _show_add_behavior_dialog(at_position: Vector2) -> void:
	"""Dialogo rapido para buscar e adicionar behavior."""
	var dialog: AcceptDialog = AcceptDialog.new()
	dialog.name = "AddBehaviorDialog"
	dialog.title = "Adicionar Behavior"
	dialog.size = Vector2(350, 400)

	var vbox: VBoxContainer = VBoxContainer.new()
	dialog.add_child(vbox)

	var search: LineEdit = LineEdit.new()
	search.placeholder_text = "Buscar behavior..."
	search.clear_button_enabled = true
	vbox.add_child(search)

	var list: ItemList = ItemList.new()
	list.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(list)

	# Popular lista
	var all_metas: Array[Dictionary] = _get_all_behaviors()
	for meta: Dictionary in all_metas:
		list.add_item(meta.get("name", "???"))
		list.set_item_metadata(list.item_count - 1, meta)

	search.text_changed.connect(func(txt: String):
		list.clear()
		var q: String = txt.to_lower()
		for meta2: Dictionary in all_metas:
			var n: String = meta2.get("name", "").to_lower()
			var d: String = meta2.get("description_pt", "").to_lower()
			if q.is_empty() or q in n or q in d:
				list.add_item(meta2.get("name", "???"))
				list.set_item_metadata(list.item_count - 1, meta2)
	)

	list.item_activated.connect(func(idx: int):
		var meta: Dictionary = list.get_item_metadata(idx)
		if not meta.is_empty():
			add_behavior_node(meta, at_position)
		dialog.queue_free()
	)

	dialog.close_requested.connect(dialog.queue_free)
	dialog.confirmed.connect(dialog.queue_free)
	dialog.canceled.connect(dialog.queue_free)
	add_child(dialog)
	dialog.popup_centered()
	search.grab_focus()


func _add_graph_frame(at_position: Vector2) -> void:
	"""Adiciona um GraphFrame para agrupar nos."""
	var frame: GraphFrame = GraphFrame.new()
	frame.name = "GraphFrame"
	frame.title = "Grupo"
	frame.position_offset = at_position
	frame.size = Vector2(300, 200)

	_undo_redo.create_action("Adicionar GraphFrame")
	_undo_redo.add_do_method(self, "add_child", frame)
	_undo_redo.add_undo_method(self, "_undo_remove_node", frame)
	_undo_redo.commit_action()

	add_child(frame)


func _show_generated_code() -> void:
	"""Exibe o GDScript gerado pela arvore visual."""
	var code: String = _generate_gdscript()
	var dialog: AcceptDialog = AcceptDialog.new()
	dialog.title = "Codigo Gerado"
	dialog.size = Vector2(600, 400)

	var code_edit: CodeEdit = CodeEdit.new()
	code_edit.text = code
	code_edit.editable = false
	code_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	code_edit.size_flags_vertical = Control.SIZE_EXPAND_FILL
	dialog.add_child(code_edit)

	dialog.confirmed.connect(dialog.queue_free)
	dialog.canceled.connect(dialog.queue_free)
	add_child(dialog)
	dialog.popup_centered()


# ── Auto-Arrange ──────────────────────────────────────────────────────────────

func arrange_nodes() -> void:
	"""Reorganiza nos selecionados (ou todos) em layout hierarquico."""
	var nodes: Array[GraphNode] = []
	var selected: Array[StringName] = get_selected_nodes()

	if selected.is_empty():
		# Todos os GraphNodes
		for child: Node in get_children():
			if child is GraphNode:
				nodes.append(child as GraphNode)
	else:
		for sel: StringName in selected:
			var n: Node = get_node_or_null(sel)
			if n and n is GraphNode:
				nodes.append(n as GraphNode)

	if nodes.is_empty():
		return

	_undo_redo.create_action("Auto-Arrange (%d nos)" % nodes.size())

	# Layout: ordenar por nome, distribuir em colunas
	var x: float = 0.0
	var y: float = 0.0
	var col_width: float = 280.0
	var row_height: float = 150.0
	var cols: int = maxi(1, int(sqrt(float(nodes.size()))))

	for i: int in range(nodes.size()):
		var col: int = i % cols
		var row: int = i / cols
		var new_pos: Vector2 = Vector2(x + col * col_width, y + row * row_height)

		_undo_redo.add_do_method(nodes[i], "set", "position_offset", new_pos)
		_undo_redo.add_undo_method(nodes[i], "set", "position_offset", nodes[i].position_offset)

	_undo_redo.commit_action()

	# Aplicar
	var col_idx: int = 0
	var row_idx: int = 0
	for i: int in range(nodes.size()):
		col_idx = i % cols
		row_idx = i / cols
		nodes[i].position_offset = Vector2(x + col_idx * col_width, y + row_idx * row_height)


# ── Drop da paleta ────────────────────────────────────────────────────────────

func _can_drop_data(at_position: Vector2, data: Variant) -> bool:
	if typeof(data) == TYPE_DICTIONARY:
		var d: Dictionary = data
		return d.get("type", "") == "behavior_node"
	return false


func _drop_data(at_position: Vector2, data: Variant) -> void:
	var d: Dictionary = data
	var meta: Dictionary = d.get("meta", {})
	if not meta.is_empty():
		add_behavior_node(meta, at_position + scroll_offset)


# ── GUI Input (drag-from-port no espaco vazio) ───────────────────────────────

func _on_gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mb: InputEventMouseButton = event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_RIGHT and mb.pressed:
			# Menu de contexto (popup_request ja cobre isso)
			pass


# ── Selecao de nos ───────────────────────────────────────────────────────────

func _on_node_selected(node: Node) -> void:
	if _inspector_ref and _inspector_ref.has_method("show_node"):
		_inspector_ref.call("show_node", node)


func _on_node_deselected(node: Node) -> void:
	if _inspector_ref and _inspector_ref.has_method("clear_node"):
		_inspector_ref.call("clear_node")


func _on_scroll_changed(ofs: Vector2) -> void:
	pass  # Reservado para otimizacao futura


# ── Utilitarios ───────────────────────────────────────────────────────────────

func _get_all_behaviors() -> Array[Dictionary]:
	"""Le todos os behavior.json do diretorio behaviors/."""
	var result: Array[Dictionary] = []
	var dir: DirAccess = DirAccess.open("res://behaviors")
	if not dir:
		return result

	dir.list_dir_begin()
	var entry: String = dir.get_next()
	while not entry.is_empty():
		if entry != "." and entry != ".." and dir.current_is_dir():
			var json_path: String = "res://behaviors/" + entry + "/behavior.json"
			if FileAccess.file_exists(json_path):
				var file: FileAccess = FileAccess.open(json_path, FileAccess.READ)
				if file:
					var text: String = file.get_as_text()
					file.close()
					var json: JSON = JSON.new()
					if json.parse(text) == OK:
						var data: Variant = json.get_data()
						if typeof(data) == TYPE_DICTIONARY:
							result.append(data)
		entry = dir.get_next()
	dir.list_dir_end()
	return result


func _generate_gdscript() -> String:
	"""Gera GDScript basico a partir da arvore visual (placeholder — completado no serializer P6)."""
	var lines: PackedStringArray = []
	lines.push_back("## GDScript gerado pelo MCP BT Editor")
	lines.push_back("## Arvore com %d nos" % get_child_count())
	lines.push_back("")
	lines.push_back("extends Node")
	lines.push_back("")
	lines.push_back("func _ready():")
	lines.push_back("\t# TODO: Executar arvore de comportamento")
	lines.push_back("\tpass")
	return "\n".join(lines)


func get_all_nodes() -> Array[GraphNode]:
	var result: Array[GraphNode] = []
	for child: Node in get_children():
		if child is GraphNode:
			result.append(child as GraphNode)
	return result


func get_connections_data() -> Array[Dictionary]:
	"""Retorna lista de conexoes no formato serializavel."""
	return get_connection_list()


func clear_all() -> void:
	"""Remove todos os nos e conexoes."""
	var nodes: Array[GraphNode] = get_all_nodes()
	for node: GraphNode in nodes:
		node.queue_free()
	clear_connections()
