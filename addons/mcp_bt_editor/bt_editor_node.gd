## bt_editor_node.gd — MCP BT Editor | GraphNode customizado para behaviors.
##
## Cada no representa um behavior do arsenal (249 disponiveis).
## Portas coloridas por tipo: FLOW(azul), CONDITION(amarelo), DATA(verde), EVENT(vermelho).
## Titulo, descricao e icone extraidos do behavior.json correspondente.
##
## @tutorial: https://docs.godotengine.org/en/stable/classes/class_graphnode.html

@tool
extends GraphNode

# ── Constantes de tipo de porta (devem bater com GraphEdit.add_valid_connection_type) ─
enum PortType {
	FLOW = 0,       # Sequencia de execucao — azul
	CONDITION = 1,  # Ramo sim/nao — amarelo
	DATA = 2,       # Passagem de dados (blackboard) — verde
	EVENT = 3,      # Eventos/sinais — vermelho
}

# ── Cores por tipo ────────────────────────────────────────────────────────────
const PORT_COLORS: Dictionary = {
	PortType.FLOW: Color(0.2, 0.5, 1.0),       # Azul
	PortType.CONDITION: Color(0.9, 0.7, 0.1),   # Amarelo
	PortType.DATA: Color(0.3, 0.8, 0.3),         # Verde
	PortType.EVENT: Color(0.95, 0.3, 0.1),       # Vermelho
}

# ── Metadados do behavior ─────────────────────────────────────────────────────
var behavior_name: String = ""
var behavior_category: String = ""
var behavior_signals: Array[Dictionary] = []
var behavior_parameters: Array[Dictionary] = []
var behavior_icon_color: Color = Color(0.5, 0.5, 0.5)  # Fallback

# ── Referencias ───────────────────────────────────────────────────────────────
var _slot_count: int = 0


# ── Setup ─────────────────────────────────────────────────────────────────────

func setup(meta: Dictionary) -> void:
	"""Configura o no com metadados do behavior.json."""
	behavior_name = meta.get("name", "unknown")
	behavior_category = meta.get("category", "generic")
	behavior_signals = meta.get("signals", [])
	behavior_parameters = meta.get("parameters", [])
	behavior_icon_color = _category_color(behavior_category)

	# Titulo
	title = behavior_name.capitalize()

	# Cor de destaque do titulo (via tema)
	var title_style: StyleBoxFlat = StyleBoxFlat.new()
	title_style.bg_color = Color(behavior_icon_color, 0.3)
	title_style.border_color = Color(behavior_icon_color, 0.8)
	title_style.border_width_left = 4
	add_theme_stylebox_override("titlebar", title_style)

	# Limpar slots existentes
	_clear_slots()
	_slot_count = 0

	# --- Criar ports ---

	# FLOW input (esquerda) — slot 0
	var flow_in_idx: int = _add_slot_left(PortType.FLOW, "in")
	# FLOW output (direita) — slot 0
	var flow_out_idx: int = _add_slot_right(PortType.FLOW, "out")

	# CONDITION outputs (sim/nao) — se o behavior emitir sinais de decisao
	if _has_condition_signals():
		var cond_yes_idx: int = _add_slot_right(PortType.CONDITION, "yes")
		var cond_no_idx: int = _add_slot_right(PortType.CONDITION, "no")

	# DATA inputs para parametros expostos
	for param: Dictionary in behavior_parameters:
		var param_name: String = param.get("name", "")
		if param_name.is_empty():
			continue
		var data_idx: int = _add_slot_left(PortType.DATA, param_name)

	# EVENT outputs para sinais emitidos
	for sig: Dictionary in behavior_signals:
		var sig_name: String = sig.get("name", "")
		if sig_name.is_empty():
			continue
		var event_idx: int = _add_slot_right(PortType.EVENT, sig_name)

	# Tamanho minimo
	custom_minimum_size = Vector2(180, 80 + maxi(_slot_count - 1, 0) * 24)

	# Tooltip rico
	var desc: String = meta.get("description", behavior_name)
	tooltip_text = "[%s] %s\nSinais: %s\nParametros: %s" % [
		behavior_category, desc,
		str(behavior_signals.size()), str(behavior_parameters.size())
	]


# ── Ports ─────────────────────────────────────────────────────────────────────

func _clear_slots() -> void:
	var i: int = get_slot_count() - 1
	while i >= 0:
		erase_slot(i)
		i -= 1
	_slot_count = 0


func _add_slot_left(port_type: int, label: String) -> int:
	var idx: int = _slot_count
	var dot: Texture2D = _make_dot(PORT_COLORS.get(port_type, Color.WHITE))
	# set_slot(idx, enable_left, type_left, color_left, enable_right, type_right, color_right, icon_left, icon_right)
	set_slot(idx, true, port_type, PORT_COLORS.get(port_type, Color.WHITE),
		false, 0, Color.WHITE, dot, null)
	_slot_count += 1
	return idx


func _add_slot_right(port_type: int, label: String) -> int:
	var idx: int = _slot_count
	var dot: Texture2D = _make_dot(PORT_COLORS.get(port_type, Color.WHITE))
	set_slot(idx, false, 0, Color.WHITE,
		true, port_type, PORT_COLORS.get(port_type, Color.WHITE), null, dot)
	_slot_count += 1
	return idx


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_dot(color: Color) -> Texture2D:
	"""Cria um icone circular de 12x12 com a cor especificada."""
	var img: Image = Image.create(12, 12, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	# Desenha circulo preenchido
	var cx: float = 5.5
	var cy: float = 5.5
	var r: float = 4.5
	for x: int in range(12):
		for y: int in range(12):
			var dx: float = float(x) - cx
			var dy: float = float(y) - cy
			if dx * dx + dy * dy <= r * r:
				img.set_pixel(x, y, color)
	var tex: ImageTexture = ImageTexture.create_from_image(img)
	return tex


func _has_condition_signals() -> bool:
	for sig: Dictionary in behavior_signals:
		var sig_name: String = sig.get("name", "")
		# Sinais que indicam ramo condicional
		if "detected" in sig_name or "triggered" in sig_name or \
		   "check" in sig_name or "evaluate" in sig_name or \
		   "result" in sig_name:
			return true
	return false


func _category_color(cat: String) -> Color:
	"""Cor por categoria de behavior."""
	match cat.to_lower():
		"health", "vida", "damage", "combat":
			return Color(0.95, 0.2, 0.2)    # Vermelho
		"movement", "physics", "motion":
			return Color(0.2, 0.5, 1.0)      # Azul
		"ai", "behavior", "controller":
			return Color(0.9, 0.7, 0.1)      # Amarelo
		"ui", "interface", "hud":
			return Color(0.3, 0.8, 0.3)      # Verde
		"audio", "sound", "music":
			return Color(0.8, 0.3, 0.8)      # Roxo
		"animation", "visual", "vfx":
			return Color(0.95, 0.5, 0.1)     # Laranja
		"data", "save", "storage":
			return Color(0.4, 0.4, 0.4)      # Cinza
		_:
			return Color(0.5, 0.5, 0.5)      # Cinza medio


# ── Acesso aos metadados ──────────────────────────────────────────────────────

func get_behavior_meta() -> Dictionary:
	return {
		"name": behavior_name,
		"category": behavior_category,
		"signals": behavior_signals,
		"parameters": behavior_parameters,
	}


func get_output_port_count() -> int:
	"""Numero de ports de saida (FLOW + CONDITION + EVENT)."""
	var count: int = 0
	var slot_total: int = get_slot_count()
	for i: int in range(slot_total):
		# get_slot_type_right retorna -1 se desabilitado, 0+ se habilitado
		if get_slot_type_right(i) >= 0:
			count += 1
	return count


func get_input_port_count() -> int:
	var count: int = 0
	var slot_total: int = get_slot_count()
	for i: int in range(slot_total):
		if get_slot_type_left(i) >= 0:
			count += 1
	return count
