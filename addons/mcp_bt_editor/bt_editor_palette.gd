## bt_editor_palette.gd — MCP BT Editor | Paleta de behaviors com busca e categorias.
##
## Escaneia o diretorio behaviors/, le behavior.json de cada um,
## agrupa por categoria e oferece busca com filtro.
## Suporta drag-and-drop para criar GraphNodes no GraphEdit.
##
## @tutorial: https://docs.godotengine.org/en/stable/classes/class_tree.html

@tool
extends VBoxContainer

# ── Sinais ────────────────────────────────────────────────────────────────────

signal behavior_selected(meta: Dictionary)
signal behavior_drag_started(meta: Dictionary)

# ── Constantes ────────────────────────────────────────────────────────────────

const BEHAVIORS_PATH: String = "res://behaviors"

# Mapeamento de tag → categoria amigavel
const TAG_CATEGORY_MAP: Dictionary = {
	"health": "Vida & Dano",
	"damage": "Vida & Dano",
	"combat": "Vida & Dano",
	"movement": "Movimento",
	"physics": "Movimento",
	"motion": "Movimento",
	"ai": "IA & Comportamento",
	"behavior": "IA & Comportamento",
	"controller": "IA & Comportamento",
	"ui": "Interface",
	"interface": "Interface",
	"hud": "Interface",
	"audio": "Audio",
	"sound": "Audio",
	"music": "Audio",
	"animation": "Animacao & Visual",
	"visual": "Animacao & Visual",
	"vfx": "Animacao & Visual",
	"shader": "Animacao & Visual",
	"camera": "Camera",
	"save": "Dados & Save",
	"data": "Dados & Save",
	"storage": "Dados & Save",
	"input": "Input",
	"multiplayer": "Multiplayer",
	"network": "Multiplayer",
	"procedural": "Geracao Procedural",
	"generation": "Geracao Procedural",
	"accessibility": "Acessibilidade",
	"localization": "Localizacao",
	"modding": "Modding",
	"debug": "Debug",
	"social": "Social",
	"achievement": "Conquistas",
}

# ── Estado ────────────────────────────────────────────────────────────────────

var _tree: Tree
var _search_box: LineEdit
var _graph_edit: GraphEdit
var _behaviors_cache: Array[Dictionary] = []
var _category_items: Dictionary = {}  # categoria_name -> TreeItem


# ── Ciclo de vida ─────────────────────────────────────────────────────────────

func _ready() -> void:
	_build_ui()
	refresh()


func _build_ui() -> void:
	# Header
	var header: Label = Label.new()
	header.name = "PaletteHeader"
	header.text = "🎨 Paleta de Behaviors"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 13)
	add_child(header)

	# Busca
	_search_box = LineEdit.new()
	_search_box.name = "SearchBox"
	_search_box.placeholder_text = "Buscar behavior..."
	_search_box.clear_button_enabled = true
	_search_box.text_changed.connect(_on_search_changed)
	add_child(_search_box)

	# Tree (categorias + behaviors)
	_tree = Tree.new()
	_tree.name = "BehaviorTree"
	_tree.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_tree.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_tree.allow_rmb_select = true
	_tree.hide_root = true
	_tree.select_mode = Tree.SELECT_SINGLE
	_tree.item_selected.connect(_on_item_selected)
	_tree.item_activated.connect(_on_item_activated)
	_tree.set_drag_forwarding(_get_drag_data, Callable(), Callable())
	add_child(_tree)

	# Contador
	var counter: Label = Label.new()
	counter.name = "BehaviorCounter"
	counter.text = "0 behaviors"
	counter.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	counter.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
	add_child(counter)

	# Refresh button
	var btn_refresh: Button = Button.new()
	btn_refresh.name = "BtnRefresh"
	btn_refresh.text = "🔄 Atualizar"
	btn_refresh.pressed.connect(refresh)
	add_child(btn_refresh)


# ── API Publica ───────────────────────────────────────────────────────────────

func set_graph_edit(graph: GraphEdit) -> void:
	_graph_edit = graph


func refresh() -> void:
	"""Reescaneia behaviors/ e reconstroi a arvore."""
	_tree.clear()
	_category_items.clear()
	_behaviors_cache.clear()

	var root: TreeItem = _tree.create_item()
	var count: int = 0

	var dir: DirAccess = DirAccess.open(BEHAVIORS_PATH)
	if not dir:
		_show_empty("Diretorio behaviors/ nao encontrado.")
		return

	dir.list_dir_begin()
	var entry: String = dir.get_next()
	var entries: Array[String] = []

	while not entry.is_empty():
		if entry != "." and entry != ".." and dir.current_is_dir():
			entries.append(entry)
		entry = dir.get_next()
	dir.list_dir_end()

	entries.sort()

	for folder_name: String in entries:
		var json_path: String = BEHAVIORS_PATH + "/" + folder_name + "/behavior.json"
		if not FileAccess.file_exists(json_path):
			continue

		var meta: Dictionary = _read_behavior_json(json_path)
		if meta.is_empty():
			continue

		_behaviors_cache.append(meta)

		# Determinar categoria
		var category: String = _classify_category(meta)

		# Criar item de categoria se necessario
		var cat_item: TreeItem = _category_items.get(category, null)
		if not cat_item:
			cat_item = _tree.create_item(root)
			cat_item.set_text(0, "📁 " + category)
			cat_item.set_selectable(0, false)
			cat_item.set_custom_color(0, Color(0.7, 0.7, 0.7))
			cat_item.collapsed = false
			_category_items[category] = cat_item

		# Criar item do behavior
		var item: TreeItem = _tree.create_item(cat_item)
		item.set_text(0, meta.get("name", folder_name))
		var desc: String = meta.get("description_pt", "")
		if desc.length() > 80:
			desc = desc.substr(0, 77) + "..."
		item.set_tooltip_text(0, desc)
		item.set_metadata(0, meta)
		count += 1

	# Atualizar contador
	var counter: Label = get_node_or_null("BehaviorCounter") as Label
	if counter:
		counter.text = "%d behaviors" % count

	if count == 0:
		_show_empty("Nenhum behavior.json encontrado em behaviors/")


# ── Internals ─────────────────────────────────────────────────────────────────

func _read_behavior_json(path: String) -> Dictionary:
	var file: FileAccess = FileAccess.open(path, FileAccess.READ)
	if not file:
		return {}
	var text: String = file.get_as_text()
	file.close()
	if text.is_empty():
		return {}
	var json: JSON = JSON.new()
	var err: int = json.parse(text)
	if err != OK:
		push_warning("[BT Editor] JSON invalido: %s (linha %d)" % [path, json.get_error_line()])
		return {}
	var data: Variant = json.get_data()
	if typeof(data) != TYPE_DICTIONARY:
		return {}
	return data


func _classify_category(meta: Dictionary) -> String:
	"""Determina a categoria de um behavior a partir de tags e generos."""
	var tags: Array = meta.get("tags", [])
	var genres: Array = meta.get("genres", [])

	# Tenta classificar por tags
	for tag in tags:
		var tag_str: String = str(tag).to_lower()
		var cat: String = TAG_CATEGORY_MAP.get(tag_str, "")
		if not cat.is_empty():
			return cat

	# Tenta classificar por genero
	for genre in genres:
		var genre_str: String = str(genre).to_lower()
		match genre_str:
			"platformer": return "Movimento"
			"rpg": return "Vida & Dano"
			"puzzle": return "IA & Comportamento"
			"shooter": return "Vida & Dano"
			"racing": return "Movimento"
			"strategy": return "IA & Comportamento"
			"simulation": return "Dados & Save"

	# Fallback
	return "Outros"


func _filter_tree(query: String) -> void:
	"""Filtra a arvore pelo texto de busca."""
	var root: TreeItem = _tree.get_root()
	if not root:
		return

	var query_lower: String = query.to_lower()
	var any_visible: bool = false

	# Percorrer categorias
	var cat_item: TreeItem = root.get_first_child()
	while cat_item:
		var cat_visible: bool = false
		var behavior_item: TreeItem = cat_item.get_first_child()
		while behavior_item:
			var name: String = behavior_item.get_text(0).to_lower()
			var meta: Dictionary = behavior_item.get_metadata(0)
			var desc: String = meta.get("description_pt", "").to_lower()
			var visible: bool = query_lower.is_empty() or query_lower in name or query_lower in desc
			behavior_item.set_visible(visible)
			if visible:
				cat_visible = true
				any_visible = true
			behavior_item = behavior_item.get_next()

		cat_item.set_visible(cat_visible)
		if cat_visible and not query_lower.is_empty():
			cat_item.collapsed = false
		cat_item = cat_item.get_next()

	# Se busca ativa, expande tudo o que for visivel
	if not query_lower.is_empty():
		cat_item = root.get_first_child()
		while cat_item:
			if cat_item.is_visible(0):
				cat_item.collapsed = false
			cat_item = cat_item.get_next()


func _show_empty(msg: String) -> void:
	var counter: Label = get_node_or_null("BehaviorCounter") as Label
	if counter:
		counter.text = "0 behaviors"
	var item: TreeItem = _tree.create_item()
	item.set_text(0, msg)
	item.set_selectable(0, false)


func _get_behaviors_for_query(query: String) -> Array[Dictionary]:
	"""Retorna lista de behaviors que batem com a busca."""
	var result: Array[Dictionary] = []
	var query_lower: String = query.to_lower()
	for meta: Dictionary in _behaviors_cache:
		var name: String = meta.get("name", "").to_lower()
		var desc: String = meta.get("description_pt", "").to_lower()
		if query_lower.is_empty() or query_lower in name or query_lower in desc:
			result.append(meta)
	return result


# ── Drag & Drop ───────────────────────────────────────────────────────────────

func _get_drag_data(at_position: Vector2) -> Variant:
	var selected: TreeItem = _tree.get_selected()
	if not selected:
		return null

	var meta: Dictionary = selected.get_metadata(0)
	if meta.is_empty():
		return null

	# Preview do drag
	var preview: Label = Label.new()
	preview.text = "🧩 " + meta.get("name", "???")
	preview.add_theme_font_size_override("font_size", 12)
	_tree.set_drag_preview(preview)

	# Retorna os metadados para o destino
	behavior_drag_started.emit(meta)
	return {"type": "behavior_node", "meta": meta}


# ── Signals ───────────────────────────────────────────────────────────────────

func _on_search_changed(new_text: String) -> void:
	_filter_tree(new_text)


func _on_item_selected() -> void:
	var selected: TreeItem = _tree.get_selected()
	if not selected:
		return
	var meta: Dictionary = selected.get_metadata(0)
	if not meta.is_empty():
		behavior_selected.emit(meta)


func _on_item_activated() -> void:
	"""Duplo-clique ou Enter: criar no no centro do GraphEdit."""
	var selected: TreeItem = _tree.get_selected()
	if not selected:
		return
	var meta: Dictionary = selected.get_metadata(0)
	if meta.is_empty():
		return
	if _graph_edit:
		_create_node_in_graph(meta)


func _create_node_in_graph(meta: Dictionary) -> void:
	"""Instancia um BTEditorNode via GraphEdit.add_behavior_node (com undo/redo)."""
	if not _graph_edit:
		return
	# Delega para o grafo, que gerencia undo/redo
	if _graph_edit.has_method("add_behavior_node"):
		var offset: Vector2 = _graph_edit.scroll_offset
		var sz: Vector2 = _graph_edit.size
		var pos: Vector2 = offset + sz * 0.5 - Vector2(90, 40)
		_graph_edit.call("add_behavior_node", meta, pos)
	else:
		# Fallback: criar diretamente (sem undo/redo)
		var script_path: String = "res://addons/mcp_bt_editor/bt_editor_node.gd"
		var gd: GDScript = load(script_path) as GDScript
		if not gd:
			return
		var node: GraphNode = gd.new() as GraphNode
		if not node.has_method("setup"):
			return
		node.call("setup", meta)
		var offset2: Vector2 = _graph_edit.scroll_offset
		var sz2: Vector2 = _graph_edit.size
		node.position_offset = offset2 + sz2 * 0.5 - Vector2(90, 40)
		_graph_edit.add_child(node)
		_graph_edit.set_selected(node)
