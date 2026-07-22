## bt_editor_inspector.gd — MCP BT Editor | Inspetor de parametros do no selecionado.
##
## Exibe nome, descricao, categoria, parametros editaveis,
## sinais emitidos e dependencias do behavior selecionado no GraphEdit.
##
## @tutorial: https://docs.godotengine.org/en/stable/classes/class_control.html

@tool
extends VBoxContainer

# ── Estado ────────────────────────────────────────────────────────────────────

var _current_node: GraphNode = null
var _current_meta: Dictionary = {}
var _param_widgets: Array[Control] = []

# ── Referencias aos nos ──────────────────────────────────────────────────────

var _title_label: Label
var _desc_label: Label
var _category_label: Label
var _params_container: VBoxContainer
var _signals_label: Label
var _deps_label: Label
var _scroll: ScrollContainer


# ── Ciclo de vida ─────────────────────────────────────────────────────────────

func _ready() -> void:
	_build_ui()


func _build_ui() -> void:
	var header: Label = Label.new()
	header.name = "InspectorHeader"
	header.text = "🔍 Inspetor"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 13)
	add_child(header)

	_scroll = ScrollContainer.new()
	_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	add_child(_scroll)

	var content: VBoxContainer = VBoxContainer.new()
	content.name = "InspectorContent"
	content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(content)

	# Nome do no
	_title_label = Label.new()
	_title_label.name = "NodeTitle"
	_title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title_label.add_theme_font_size_override("font_size", 16)
	content.add_child(_title_label)

	# Categoria
	_category_label = Label.new()
	_category_label.name = "NodeCategory"
	_category_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_category_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
	content.add_child(_category_label)

	# Separador
	var sep1: HSeparator = HSeparator.new()
	content.add_child(sep1)

	# Descricao
	_desc_label = Label.new()
	_desc_label.name = "NodeDescription"
	_desc_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	_desc_label.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
	content.add_child(_desc_label)

	var sep2: HSeparator = HSeparator.new()
	content.add_child(sep2)

	# Secao de parametros
	var param_header: Label = Label.new()
	param_header.text = "📊 Parametros:"
	param_header.add_theme_font_size_override("font_size", 12)
	content.add_child(param_header)

	_params_container = VBoxContainer.new()
	_params_container.name = "ParamsContainer"
	content.add_child(_params_container)

	var sep3: HSeparator = HSeparator.new()
	content.add_child(sep3)

	# Sinais
	_signals_label = Label.new()
	_signals_label.name = "SignalsLabel"
	_signals_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	_signals_label.add_theme_font_size_override("font_size", 11)
	content.add_child(_signals_label)

	var sep4: HSeparator = HSeparator.new()
	content.add_child(sep4)

	# Dependencias
	_deps_label = Label.new()
	_deps_label.name = "DepsLabel"
	_deps_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	_deps_label.add_theme_font_size_override("font_size", 11)
	content.add_child(_deps_label)

	# Estado inicial
	clear_node()


# ── API Publica ───────────────────────────────────────────────────────────────

func show_node(node: Node) -> void:
	"""Exibe informacoes do no selecionado."""
	clear_node()

	if not node is GraphNode:
		return

	_current_node = node as GraphNode

	# Tenta ler metadados do no
	var meta: Dictionary = {}
	if _current_node.has_method("get_behavior_meta"):
		meta = _current_node.call("get_behavior_meta")
	else:
		meta = _current_node.get_meta("behavior_meta", {})

	_current_meta = meta

	if meta.is_empty():
		# No generico (reroute, expression, frame)
		_title_label.text = _current_node.name
		_category_label.text = ""
		_desc_label.text = _current_node.tooltip_text if not _current_node.tooltip_text.is_empty() else "No sem metadados."
		return

	# Popular campos
	var name_str: String = meta.get("name", _current_node.name)
	_title_label.text = name_str.capitalize()
	_category_label.text = "🏷️ " + meta.get("category", "generic")
	_desc_label.text = meta.get("description_pt", meta.get("description_en", ""))

	# Parametros
	_populate_parameters(meta.get("parameters", []))

	# Sinais
	var signals: Array = meta.get("signals", [])
	if signals.is_empty():
		_signals_label.text = "📡 Sinais: nenhum"
	else:
		var sig_text: String = "📡 Sinais:\n"
		for sig in signals:
			var sig_dict: Dictionary = sig
			sig_text += "  • " + sig_dict.get("name", "???")
			var params: Array = sig_dict.get("params", [])
			if not params.is_empty():
				var param_names: PackedStringArray = []
				for p in params:
					var p_dict: Dictionary = p
					param_names.append(p_dict.get("name", "?"))
				sig_text += "(" + ", ".join(param_names) + ")"
			sig_text += "\n"
		_signals_label.text = sig_text

	# Dependencias
	var deps: Array = meta.get("dependencies", [])
	if deps.is_empty():
		_deps_label.text = "🔗 Dependencias: nenhuma"
	else:
		_deps_label.text = "🔗 Dependencias: " + ", ".join(deps)


func clear_node() -> void:
	"""Limpa o inspetor (nenhum no selecionado)."""
	_current_node = null
	_current_meta = {}
	_clear_param_widgets()

	_title_label.text = "(Nenhum no selecionado)"
	_category_label.text = ""
	_desc_label.text = "Selecione um no no grafo para ver e editar seus parametros."
	_signals_label.text = ""
	_deps_label.text = ""


func get_current_params() -> Dictionary:
	"""Retorna os valores atuais dos parametros como dicionario."""
	var result: Dictionary = {}
	for widget: Control in _param_widgets:
		var param_name: String = widget.get_meta("param_name", "")
		if param_name.is_empty():
			continue
		var value: Variant = _read_widget_value(widget)
		result[param_name] = value
	return result


# ── Parametros UI ────────────────────────────────────────────────────────────

func _populate_parameters(params: Array) -> void:
	_clear_param_widgets()

	if params.is_empty():
		var label: Label = Label.new()
		label.text = "  (sem parametros configuraveis)"
		label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
		_params_container.add_child(label)
		_param_widgets.append(label)
		return

	for param_data in params:
		var pd: Dictionary = param_data
		var param_name: String = pd.get("name", "")
		var param_type: String = pd.get("type", "float")
		var default_val: Variant = pd.get("default", 0)
		var desc: String = pd.get("description_pt", "")
		var range_dict: Dictionary = pd.get("range", {})

		var hbox: HBoxContainer = HBoxContainer.new()
		hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL

		var name_label: Label = Label.new()
		name_label.text = param_name + ":"
		name_label.custom_minimum_size = Vector2(90, 0)
		name_label.tooltip_text = desc
		hbox.add_child(name_label)

		var widget: Control = _create_param_widget(param_type, default_val, range_dict)
		widget.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		widget.set_meta("param_name", param_name)
		widget.set_meta("param_type", param_type)
		hbox.add_child(widget)

		_params_container.add_child(hbox)
		_param_widgets.append(widget)


func _create_param_widget(p_type: String, default_val: Variant, range_d: Dictionary) -> Control:
	match p_type:
		"int":
			var spin_int: SpinBox = SpinBox.new()
			spin_int.value = float(default_val) if typeof(default_val) in [TYPE_INT, TYPE_FLOAT] else 0
			spin_int.min_value = range_d.get("min", -999999)
			spin_int.max_value = range_d.get("max", 999999)
			spin_int.step = range_d.get("step", 1)
			spin_int.rounded = true
			return spin_int
		"float":
			var spin_float: SpinBox = SpinBox.new()
			spin_float.value = float(default_val) if typeof(default_val) in [TYPE_INT, TYPE_FLOAT] else 0.0
			spin_float.min_value = range_d.get("min", -999999.0)
			spin_float.max_value = range_d.get("max", 999999.0)
			spin_float.step = range_d.get("step", 0.1)
			spin_float.rounded = false
			return spin_float
		"bool":
			var check: CheckBox = CheckBox.new()
			check.button_pressed = bool(default_val)
			return check
		"String":
			var line_str: LineEdit = LineEdit.new()
			line_str.text = str(default_val) if default_val != null else ""
			return line_str
		"Color":
			var picker: ColorPickerButton = ColorPickerButton.new()
			if typeof(default_val) == TYPE_COLOR:
				picker.color = default_val
			return picker
		"Vector2":
			return _create_vector_widget(2, default_val, range_d)
		"Vector3":
			return _create_vector_widget(3, default_val, range_d)
		_:
			var line_def: LineEdit = LineEdit.new()
			line_def.text = str(default_val) if default_val != null else ""
			line_def.editable = false
			return line_def


func _create_vector_widget(components: int, default_val: Variant, range_d: Dictionary) -> Control:
	var hbox: HBoxContainer = HBoxContainer.new()
	for i: int in range(components):
		var spin: SpinBox = SpinBox.new()
		spin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		spin.min_value = range_d.get("min", -999999.0)
		spin.max_value = range_d.get("max", 999999.0)
		spin.step = range_d.get("step", 1.0)
		# Valor default
		if typeof(default_val) == TYPE_VECTOR2 and components == 2:
			var v2: Vector2 = default_val
			spin.value = v2.x if i == 0 else v2.y
		elif typeof(default_val) == TYPE_VECTOR3 and components == 3:
			var v3: Vector3 = default_val
			spin.value = [v3.x, v3.y, v3.z][i]
		hbox.add_child(spin)
	return hbox


func _read_widget_value(widget: Control) -> Variant:
	if widget is SpinBox:
		var sp1: SpinBox = widget as SpinBox
		return int(sp1.value) if sp1.rounded else sp1.value
	elif widget is CheckBox:
		return (widget as CheckBox).button_pressed
	elif widget is LineEdit:
		return (widget as LineEdit).text
	elif widget is ColorPickerButton:
		return (widget as ColorPickerButton).color
	elif widget is Label:
		return null
	elif widget is HBoxContainer:
		# Vector widget
		var hb: HBoxContainer = widget as HBoxContainer
		var comps: Array[float] = []
		for child: Node in hb.get_children():
			if child is SpinBox:
				var sp2: SpinBox = child as SpinBox
				comps.append(sp2.value if not sp2.rounded else int(sp2.value))
		if comps.size() == 2:
			return Vector2(comps[0], comps[1])
		elif comps.size() == 3:
			return Vector3(comps[0], comps[1], comps[2])
	return null


func _clear_param_widgets() -> void:
	for widget: Control in _param_widgets:
		if widget and is_instance_valid(widget):
			widget.queue_free()
	_param_widgets.clear()

	# Limpar tambem os containers (hboxes)
	for child: Node in _params_container.get_children():
		child.queue_free()
