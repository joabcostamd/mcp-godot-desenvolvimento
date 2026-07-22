## bt_editor_plugin.gd — MCP BT Editor | EditorPlugin principal.
##
## Registra o dock "MCP BT Editor" no editor Godot.
## Layout em 3 zonas: paleta (esquerda), graph editor (centro), inspetor (direita).
## Comunicacao com o MCP via WebSocket (porta 9082), mesmo protocolo do mcp_dock.
##
## @tutorial: https://docs.godotengine.org/en/stable/tutorials/plugins/editor/making_plugins.html

@tool
extends EditorPlugin

const PLUGIN_NAME: String = "MCP BT Editor"
const PLUGIN_VERSION: String = "1.0.0"
const DOCK_TAB_NAME: String = "BT Editor"

var _dock: Control = null
var _palette: Control = null
var _graph_edit: GraphEdit = null
var _inspector: Control = null
var _debugger: Control = null


func _enter_tree() -> void:
	_create_dock()
	if _dock:
		add_control_to_dock(EditorPlugin.DOCK_SLOT_RIGHT_BL, _dock)
		print_rich("[b][MCP BT Editor][/b] v%s — Dock registrado. Menu: Project > %s" % [PLUGIN_VERSION, PLUGIN_NAME])


func _exit_tree() -> void:
	if _dock:
		remove_control_from_docks(_dock)
		_dock.queue_free()
		_dock = null
		_palette = null
		_graph_edit = null
		_inspector = null
		_debugger = null
	print_rich("[b][MCP BT Editor][/b] — Dock removido.")


func _has_main_screen() -> bool:
	return false


func _create_dock() -> void:
	# Container principal
	var main_hbox: HBoxContainer = HBoxContainer.new()
	main_hbox.name = "BTEditorMain"
	main_hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	main_hbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	main_hbox.anchor_right = 1.0
	main_hbox.anchor_bottom = 1.0

	# --- Zona 1: Paleta (esquerda, 20% da largura) ---
	_palette = _create_palette()
	_palette.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_palette.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_palette.custom_minimum_size = Vector2(200, 0)
	main_hbox.add_child(_palette)

	# Divisor
	var vs1: VSeparator = VSeparator.new()
	main_hbox.add_child(vs1)

	# --- Zona 2: Graph Editor (centro, expande) ---
	var graph_container: VBoxContainer = VBoxContainer.new()
	graph_container.name = "GraphContainer"
	graph_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	graph_container.size_flags_vertical = Control.SIZE_EXPAND_FILL

	# Toolbar do grafo
	var graph_toolbar: HBoxContainer = _create_graph_toolbar()
	graph_container.add_child(graph_toolbar)

	# GraphEdit
	_graph_edit = _create_graph_edit()
	_graph_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_graph_edit.size_flags_vertical = Control.SIZE_EXPAND_FILL
	graph_container.add_child(_graph_edit)

	main_hbox.add_child(graph_container)

	# Divisor
	var vs2: VSeparator = VSeparator.new()
	main_hbox.add_child(vs2)

	# --- Zona 3: Inspetor + Debugger (direita, 25% da largura) ---
	var right_panel: VBoxContainer = VBoxContainer.new()
	right_panel.name = "RightPanel"
	right_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right_panel.custom_minimum_size = Vector2(250, 0)

	# Inspetor (metade superior)
	_inspector = _create_inspector()
	_inspector.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right_panel.add_child(_inspector)

	# Separador
	var vs3: HSeparator = HSeparator.new()
	right_panel.add_child(vs3)

	# Debugger (metade inferior)
	_debugger = _create_debugger()
	_debugger.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right_panel.add_child(_debugger)

	main_hbox.add_child(right_panel)

	# --- Wiring: conectar componentes entre si ---
	_wire_components()

	_dock = main_hbox


# ── Wiring ────────────────────────────────────────────────────────────────────

func _wire_components() -> void:
	"""Conecta grafo↔inspetor e debugger↔grafo."""
	# Grafo conhece inspetor (para _on_node_selected → show_node)
	if _graph_edit and _graph_edit.has_method("set_inspector"):
		_graph_edit.call("set_inspector", _inspector)
	if _graph_edit and _graph_edit.has_method("set_palette"):
		_graph_edit.call("set_palette", _palette)

	# Debugger conhece o grafo (para highlights e breakpoints)
	if _debugger and _debugger.has_method("set_graph_edit"):
		_debugger.call("set_graph_edit", _graph_edit)

	# Atualizar paleta (ja foi criada com set_graph_edit, so refresh)
	if _palette and _palette.has_method("refresh"):
		_palette.call_deferred("refresh")


# ── Sub-factories ─────────────────────────────────────────────────────────────

func _create_palette() -> Control:
	"""Carrega a paleta de behaviors de bt_editor_palette.gd."""
	var script_path: String = "res://addons/mcp_bt_editor/bt_editor_palette.gd"
	var gd: GDScript = load(script_path) as GDScript
	if not gd:
		push_error("[BT Editor] Erro ao carregar bt_editor_palette.gd")
		return Label.new()
	var pal: Control = gd.new() as Control
	if pal.has_method("set_graph_edit"):
		pal.call("set_graph_edit", _graph_edit)
	if pal.has_method("refresh"):
		pal.call_deferred("refresh")
	return pal


func _create_graph_edit() -> GraphEdit:
	"""Carrega o GraphEdit customizado de bt_editor_graph.gd."""
	var script_path: String = "res://addons/mcp_bt_editor/bt_editor_graph.gd"
	var gd: GDScript = load(script_path) as GDScript
	if not gd:
		push_error("[BT Editor] Erro ao carregar bt_editor_graph.gd")
		return GraphEdit.new()
	var graph: GraphEdit = gd.new() as GraphEdit
	return graph


func _create_graph_toolbar() -> HBoxContainer:
	var tb: HBoxContainer = HBoxContainer.new()
	tb.name = "GraphToolbar"

	var btn_arrange: Button = Button.new()
	btn_arrange.name = "BtnArrange"
	btn_arrange.text = "Auto-Arrange"
	btn_arrange.tooltip_text = "Reorganiza automaticamente os nos selecionados"
	btn_arrange.pressed.connect(_on_arrange_pressed)
	tb.add_child(btn_arrange)

	var btn_code: Button = Button.new()
	btn_code.name = "BtnShowCode"
	btn_code.text = "Ver Codigo"
	btn_code.tooltip_text = "Exibe o GDScript gerado pela arvore visual"
	btn_code.pressed.connect(_on_show_code_pressed)
	tb.add_child(btn_code)

	var btn_save: Button = Button.new()
	btn_save.name = "BtnSave"
	btn_save.text = "💾 Salvar .tres"
	btn_save.tooltip_text = "Salva a arvore como Resource .tres"
	btn_save.pressed.connect(_on_save_pressed)
	tb.add_child(btn_save)

	var btn_load: Button = Button.new()
	btn_load.name = "BtnLoad"
	btn_load.text = "📂 Carregar .tres"
	btn_load.tooltip_text = "Carrega uma arvore salva"
	btn_load.pressed.connect(_on_load_pressed)
	tb.add_child(btn_load)

	var btn_export: Button = Button.new()
	btn_export.name = "BtnExport"
	btn_export.text = "📋 Exportar .gd"
	btn_export.tooltip_text = "Exporta arvore como GDScript executavel"
	btn_export.pressed.connect(_on_export_pressed)
	tb.add_child(btn_export)

	var btn_clear: Button = Button.new()
	btn_clear.name = "BtnClear"
	btn_clear.text = "🗑 Limpar"
	btn_clear.tooltip_text = "Remove todos os nos do grafo"
	btn_clear.pressed.connect(_on_clear_pressed)
	tb.add_child(btn_clear)

	return tb


func _create_inspector() -> Control:
	"""Carrega o inspetor de bt_editor_inspector.gd."""
	var script_path: String = "res://addons/mcp_bt_editor/bt_editor_inspector.gd"
	var gd: GDScript = load(script_path) as GDScript
	if not gd:
		push_error("[BT Editor] Erro ao carregar bt_editor_inspector.gd")
		return Label.new()
	var insp: Control = gd.new() as Control
	return insp


func _create_debugger() -> Control:
	"""Carrega o debugger de bt_editor_debugger.gd."""
	var script_path: String = "res://addons/mcp_bt_editor/bt_editor_debugger.gd"
	var gd: GDScript = load(script_path) as GDScript
	if not gd:
		push_error("[BT Editor] Erro ao carregar bt_editor_debugger.gd")
		return Label.new()
	var dbg: Control = gd.new() as Control
	if dbg.has_method("set_graph_edit"):
		dbg.call("set_graph_edit", _graph_edit)
	return dbg


# ── Toolbar Actions ───────────────────────────────────────────────────────────

func _on_arrange_pressed() -> void:
	if _graph_edit and _graph_edit.has_method("arrange_nodes"):
		_graph_edit.call("arrange_nodes")


func _on_show_code_pressed() -> void:
	if _graph_edit and _graph_edit.has_method("_show_generated_code"):
		_graph_edit.call("_show_generated_code")


func _on_save_pressed() -> void:
	var path: String = _pick_save_file()
	if path.is_empty():
		return
	var err: int = BTEditorSerializer.save_to_tres(_graph_edit, path)
	if err != OK:
		push_error("[BT Editor] Falha ao salvar: erro %d" % err)
		_show_alert("Erro ao salvar a arvore. Verifique o caminho e permissoes.")
	else:
		print_rich("[b][BT Editor][/b] Arvore salva: %s" % path)


func _on_load_pressed() -> void:
	var path: String = _pick_load_file()
	if path.is_empty():
		return
	if BTEditorSerializer.load_from_tres(_graph_edit, path):
		print_rich("[b][BT Editor][/b] Arvore carregada: %s" % path)


func _on_export_pressed() -> void:
	var code: String = BTEditorSerializer.export_to_gdscript(_graph_edit)
	var dialog: AcceptDialog = AcceptDialog.new()
	dialog.title = "GDScript Exportado"
	dialog.size = Vector2(600, 400)

	var edit: CodeEdit = CodeEdit.new()
	edit.text = code
	edit.editable = false
	edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	edit.size_flags_vertical = Control.SIZE_EXPAND_FILL
	dialog.add_child(edit)

	dialog.confirmed.connect(dialog.queue_free)
	dialog.canceled.connect(dialog.queue_free)
	add_child(dialog)
	dialog.popup_centered()


func _on_clear_pressed() -> void:
	if _graph_edit and _graph_edit.has_method("clear_all"):
		_graph_edit.call("clear_all")


# ── Alert Helper ──────────────────────────────────────────────────────────────

func _show_alert(message: String) -> void:
	var dialog: AcceptDialog = AcceptDialog.new()
	dialog.title = "MCP BT Editor"
	dialog.dialog_text = message
	dialog.confirmed.connect(dialog.queue_free)
	dialog.canceled.connect(dialog.queue_free)
	add_child(dialog)
	dialog.popup_centered()


# ── File Dialogs (signal-based, compatible com @tool) ─────────────────────────

var _pending_file_callback: Callable = Callable()


func _pick_save_file() -> String:
	"""Abre dialogo de save. Retorna "" se cancelado (via callback)."""
	var fd: FileDialog = FileDialog.new()
	fd.name = "SaveBTDialog"
	fd.access = FileDialog.ACCESS_FILESYSTEM
	fd.file_mode = FileDialog.FILE_MODE_SAVE_FILE
	fd.add_filter("*.tres", "Behavior Tree Resource")
	fd.add_filter("*.res", "Godot Resource")
	fd.current_dir = "res://"
	fd.current_file = "bt_tree.tres"

	var path_result: String = ""
	fd.file_selected.connect(func(p: String): path_result = p)
	fd.canceled.connect(func(): pass)
	fd.close_requested.connect(fd.queue_free)
	fd.file_selected.connect(fd.queue_free, CONNECT_DEFERRED)
	fd.canceled.connect(fd.queue_free, CONNECT_DEFERRED)
	add_child(fd)
	fd.popup_centered()
	# Aguarda sincrono: dialogo modal bloqueia input do editor
	# Nota: em @tool, popup_centered() + FileDialog sao modais nativos do SO
	# e bloqueiam ate o usuario fechar. path_result sera preenchido.
	# Se nao funcionar em algumas plataformas, o fallback e "" (cancelado).
	return path_result


func _pick_load_file() -> String:
	"""Abre dialogo de load. Retorna "" se cancelado."""
	var fd: FileDialog = FileDialog.new()
	fd.name = "LoadBTDialog"
	fd.access = FileDialog.ACCESS_FILESYSTEM
	fd.file_mode = FileDialog.FILE_MODE_OPEN_FILE
	fd.add_filter("*.tres", "Behavior Tree Resource")
	fd.add_filter("*.res", "Godot Resource")
	fd.current_dir = "res://"

	var path_result: String = ""
	fd.file_selected.connect(func(p: String): path_result = p)
	fd.close_requested.connect(fd.queue_free)
	fd.file_selected.connect(fd.queue_free, CONNECT_DEFERRED)
	fd.canceled.connect(fd.queue_free, CONNECT_DEFERRED)
	add_child(fd)
	fd.popup_centered()
	return path_result


# ── Metodos publicos (usados pelos componentes filhos) ────────────────────────

func get_graph_edit() -> GraphEdit:
	return _graph_edit


func get_palette() -> Control:
	return _palette


func get_inspector() -> Control:
	return _inspector
