## bt_editor_serializer.gd — MCP BT Editor | Salvar/Carregar .tres e Exportar GDScript.
##
## Formato .tres: Resource customizado que armazena nos, conexoes e metadados.
## Export GDScript: gera codigo compativel com o executor behavior_tree.gd existente.
##
## @tutorial: https://docs.godotengine.org/en/stable/classes/class_resource.html

@tool
class_name BTEditorSerializer
extends RefCounted

# ── Constantes ────────────────────────────────────────────────────────────────

const RESOURCE_SCRIPT_PATH: String = "res://addons/mcp_bt_editor/bt_tree_resource.gd"

# ── Tipos de porta ───────────────────────────────────────────────────────────

enum PortType {
	FLOW = 0,
	CONDITION = 1,
	DATA = 2,
	EVENT = 3,
}


# ── Serializacao → .tres ─────────────────────────────────────────────────────

static func save_to_tres(graph: GraphEdit, path: String) -> int:
	"""Salva o grafo como Resource .tres. Retorna OK ou erro."""
	var data: Dictionary = _serialize_graph(graph)
	var res: BTTreeResource = BTTreeResource.new()
	res.tree_data = data

	var err: int = ResourceSaver.save(res, path)
	if err != OK:
		push_error("[BT Editor] Erro ao salvar .tres: %d" % err)
	return err


static func load_from_tres(graph: GraphEdit, path: String) -> bool:
	"""Carrega um .tres e reconstroi o grafo. Retorna true se ok."""
	if not FileAccess.file_exists(path):
		push_error("[BT Editor] Arquivo nao encontrado: %s" % path)
		return false

	var res: Resource = ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE)
	if not res or not res is BTTreeResource:
		push_error("[BT Editor] Arquivo invalido ou nao e BTTreeResource: %s" % path)
		return false

	var bt_res: BTTreeResource = res as BTTreeResource
	var data: Dictionary = bt_res.tree_data
	if data.is_empty():
		return false

	# Limpar grafo atual
	graph.clear_all()

	# Reconstruir nos
	var nodes_data: Array = data.get("nodes", [])
	var node_map: Dictionary = {}  # node_id -> GraphNode

	for nd in nodes_data:
		var nd_dict: Dictionary = nd
		var node_type: String = nd_dict.get("type", "behavior")
		var pos: Vector2 = str_to_var("Vector2" + str(nd_dict.get("position", Vector2.ZERO)))

		var gn: GraphNode
		match node_type:
			"behavior":
				var meta: Dictionary = nd_dict.get("meta", {})
				gn = graph.add_behavior_node(meta, pos)
			"reroute":
				gn = graph.add_reroute_node(pos)
			"expression":
				var expr: String = nd_dict.get("expression", "")
				gn = graph.add_expression_node(pos, expr)
			"frame":
				gn = _add_frame(graph, pos, nd_dict)
			_:
				continue

		if gn:
			var node_id: String = nd_dict.get("id", "")
			if not node_id.is_empty():
				node_map[node_id] = gn
				gn.name = node_id

	# Reconstruir conexoes
	var connections: Array = data.get("connections", [])
	for conn in connections:
		var c: Dictionary = conn
		var from_id: String = c.get("from_node", "")
		var from_port: int = c.get("from_port", 0)
		var to_id: String = c.get("to_node", "")
		var to_port: int = c.get("to_port", 0)

		var from_node: GraphNode = node_map.get(from_id, null)
		var to_node: GraphNode = node_map.get(to_id, null)
		if from_node and to_node:
			graph.connect_node(from_node.name, from_port, to_node.name, to_port)

	return true


# ── Export → GDScript ─────────────────────────────────────────────────────────

static func export_to_gdscript(graph: GraphEdit, class_name: String = "") -> String:
	"""Gera GDScript executavel a partir da arvore visual."""
	var lines: PackedStringArray = []
	var indent: String = ""

	var name_str: String = class_name
	if name_str.is_empty():
		name_str = "GeneratedBT"

	lines.push_back("## %s — Gerado pelo MCP BT Editor" % name_str)
	lines.push_back("## NAO EDITE MANUALMENTE — use o editor visual.")
	lines.push_back("")
	lines.push_back("@tool")
	lines.push_back("extends Node")
	lines.push_back("")

	# Variaveis
	lines.push_back("var _running: bool = false")
	lines.push_back("var _tick_timer: float = 0.0")
	lines.push_back("@export var tick_rate: float = 0.1")
	lines.push_back("")

	# Sinais
	lines.push_back("signal tree_started()")
	lines.push_back("signal tree_stopped()")
	lines.push_back("signal node_executed(node_name: String, status: String)")
	lines.push_back("")

	# Metodos de controle
	lines.push_back("func start() -> void:")
	lines.push_back("\tif _running: return")
	lines.push_back("\t_running = true")
	lines.push_back("\ttree_started.emit()")
	lines.push_back("")
	lines.push_back("func stop() -> void:")
	lines.push_back("\tif not _running: return")
	lines.push_back("\t_running = false")
	lines.push_back("\ttree_stopped.emit()")
	lines.push_back("")
	lines.push_back("func is_running() -> bool: return _running")
	lines.push_back("")

	# _ready
	lines.push_back("func _ready() -> void:")
	lines.push_back("\tpass")
	lines.push_back("")

	# _process
	lines.push_back("func _process(delta: float) -> void:")
	lines.push_back("\tif not _running: return")
	lines.push_back("\t_tick_timer += delta")
	lines.push_back("\tif _tick_timer >= tick_rate:")
	lines.push_back("\t\t_tick_timer = 0.0")
	lines.push_back("\t\t_tick()")
	lines.push_back("")

	# _tick — executa a arvore
	lines.push_back("func _tick() -> void:")
	lines.push_back("\t_execute_tree()")
	lines.push_back("")

	# _execute_tree — percorre nos em ordem topologica
	lines.push_back("func _execute_tree() -> String:")
	var execution_order: Array[Dictionary] = _get_execution_order(graph)
	if execution_order.is_empty():
		lines.push_back("\treturn \"success\"")
	else:
		lines.push_back("\tvar status: String = \"success\"")
		for step: Dictionary in execution_order:
			var node_name: String = step.get("name", "unknown")
			var behavior: String = step.get("behavior", "")
			var action: String = step.get("action", "pass")
			lines.push_back("\t# No: %s" % node_name)
			lines.push_back("\tnode_executed.emit(\"%s\", \"running\")" % node_name)
			if not behavior.is_empty():
				lines.push_back("\t# Behavior: %s — verificar se o no pai tem metodo" % behavior)
				lines.push_back("\t# if has_method(\"%s\"): %s()" % [action, action])
			lines.push_back("\tnode_executed.emit(\"%s\", \"success\")" % node_name)
		lines.push_back("\treturn status")

	lines.push_back("")
	lines.push_back("func _get_configuration_warnings() -> PackedStringArray:")
	lines.push_back("\tvar w: PackedStringArray = []")
	lines.push_back("\treturn w")

	return "\n".join(lines)


# ── Internals ─────────────────────────────────────────────────────────────────

static func _serialize_graph(graph: GraphEdit) -> Dictionary:
	"""Serializa o grafo completo para dicionario."""
	var nodes: Array[Dictionary] = []
	var connections: Array[Dictionary] = []

	# Serializar nos
	for child: Node in graph.get_children():
		if not child is GraphNode:
			continue
		var gn: GraphNode = child as GraphNode
		var nd: Dictionary = {
			"id": gn.name,
			"position": var_to_str(gn.position_offset),
			"size": var_to_str(gn.size),
		}

		# Determinar tipo
		if gn.has_method("get_behavior_meta"):
			nd["type"] = "behavior"
			nd["meta"] = gn.call("get_behavior_meta")
		elif "expression" in str(gn.get_meta("node_type", "")):
			nd["type"] = "expression"
			nd["expression"] = gn.get_meta("expression", "")
		elif gn is GraphFrame:
			nd["type"] = "frame"
			nd["title"] = (gn as GraphFrame).title
		else:
			nd["type"] = "reroute"

		# Parametros atuais (se for behavior)
		if nd["type"] == "behavior":
			nd["params"] = {}  # TODO: ler do inspetor quando integrado

		nodes.append(nd)

	# Serializar conexoes
	var conn_list: Array[Dictionary] = graph.get_connection_list()
	for conn: Dictionary in conn_list:
		connections.append({
			"from_node": conn.get("from_node", ""),
			"from_port": conn.get("from_port", 0),
			"to_node": conn.get("to_node", ""),
			"to_port": conn.get("to_port", 0),
		})

	return {
		"version": "1.0.0",
		"nodes": nodes,
		"connections": connections,
	}


static func _add_frame(graph: GraphEdit, pos: Vector2, data: Dictionary) -> GraphNode:
	var frame: GraphFrame = GraphFrame.new()
	frame.name = data.get("id", "GraphFrame")
	frame.title = data.get("title", "Grupo")
	frame.position_offset = pos
	graph.add_child(frame)
	return frame


static func _get_execution_order(graph: GraphEdit) -> Array[Dictionary]:
	"""Topological sort dos nos do grafo para ordem de execucao."""
	var result: Array[Dictionary] = []
	var conns: Array[Dictionary] = graph.get_connection_list()

	# Construir grafo de dependencias
	var in_degree: Dictionary = {}
	var adj: Dictionary = {}

	for child: Node in graph.get_children():
		if child is GraphNode:
			var gn: GraphNode = child as GraphNode
			var name: String = gn.name
			if not in_degree.has(name):
				in_degree[name] = 0
				adj[name] = []

	for conn: Dictionary in conns:
		var from_n: String = conn.get("from_node", "")
		var to_n: String = conn.get("to_node", "")
		if adj.has(from_n):
			adj[from_n].append(to_n)
		if in_degree.has(to_n):
			in_degree[to_n] = in_degree.get(to_n, 0) + 1

	# BFS Kahn
	var queue: Array[String] = []
	for node_name: String in in_degree.keys():
		if in_degree[node_name] == 0:
			queue.append(node_name)

	while not queue.is_empty():
		var current: String = queue.pop_front()
		var gn: Node = graph.get_node_or_null(current)
		if gn and gn is GraphNode:
			var meta: Dictionary = {}
			var gnode: GraphNode = gn as GraphNode
			if gnode.has_method("get_behavior_meta"):
				meta = gnode.call("get_behavior_meta")
			result.append({
				"name": current,
				"behavior": meta.get("name", ""),
				"action": meta.get("name", "pass"),
			})

		if adj.has(current):
			for neighbor: String in adj[current]:
				in_degree[neighbor] = in_degree.get(neighbor, 1) - 1
				if in_degree[neighbor] == 0:
					queue.append(neighbor)

	return result
