## plugin.gd — MCP Dock | EditorPlugin para o painel visual.
##
## Registra o dock no editor Godot. O dock em si está em dock.tscn/dock.gd.
## Comunicação com o MCP via WebSocket (porta 9082), mesmo protocolo do mcp_addon.
##
## @tutorial: https://docs.godotengine.org/en/stable/tutorials/plugins/editor/making_plugins.html

@tool
extends EditorPlugin

const DOCK_NAME: String = "MCP"
const PLUGIN_VERSION: String = "1.0.0"

var _dock: Control


func _enter_tree() -> void:
	_dock = _create_dock()
	if _dock:
		add_control_to_dock(EditorPlugin.DOCK_SLOT_RIGHT_BL, _dock)
		print_rich("[b][MCP Dock][/b] v%s — Painel registrado." % PLUGIN_VERSION)


func _exit_tree() -> void:
	if _dock:
		remove_control_from_docks(_dock)
		_dock.queue_free()
		_dock = null
	print_rich("[b][MCP Dock][/b] — Painel removido.")


func _has_main_screen() -> bool:
	return false


func _create_dock() -> Control:
	var dock_scene: PackedScene = load("res://addons/mcp_dock/dock.tscn")
	if not dock_scene:
		push_error("[MCP Dock] Erro: dock.tscn não encontrado em addons/mcp_dock/")
		return null
	return dock_scene.instantiate()
