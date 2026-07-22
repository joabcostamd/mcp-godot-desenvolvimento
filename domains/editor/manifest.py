"""domains/editor/manifest.py — F6.2."""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="editor", tool_name="editor_manage", title="Editor", namespace="project", version="1.0.0",
    description="Gerencia o editor Godot ao vivo via addon bridge.\nQUANDO USAR: para manipular cenas e nós com UndoRedo nativo.\nQUANDO NÃO USAR: para cenas em arquivo (use scene_manage/node_manage).\nPRÉ-CONDIÇÕES: addon mcp_addon instalado, editor Godot aberto.",
    phases=[Phase.PROTOTIPO, Phase.CONTEUDO], annotations={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("connect", handlers.addon_connect, "Conecta ao addon", {}, [{}]),
         OpSpec("disconnect", handlers.addon_disconnect, "Desconecta", {}, [{}]),
         OpSpec("is_available", handlers.addon_is_available, "Verifica disponibilidade", {}, [{}]),
         OpSpec("ping", handlers.addon_ping, "Ping", {}, [{}]),
         OpSpec("create_node", handlers.addon_create_node, "Cria nó ao vivo", {"parent_path": {"type": "string", "required": False}, "node_type": {"type": "string", "required": False}, "node_name": {"type": "string", "required": False}}, [{"node_type": "Sprite2D", "node_name": "Player"}]),
         OpSpec("delete_node", handlers.addon_delete_node, "Remove nó", {"node_path": {"type": "string", "required": True}}, [{"node_path": "./OldNode"}]),
         OpSpec("set_property", handlers.addon_set_property, "Define propriedade", {"node_path": {"type": "string", "required": True}, "property_name": {"type": "string", "required": True}}, [{"node_path": "./Player", "property_name": "position"}]),
         OpSpec("reparent_node", handlers.addon_reparent_node, "Re-parenta", {"node_path": {"type": "string", "required": True}, "new_parent": {"type": "string", "required": True}}, [{"node_path": "./Enemy", "new_parent": "./Enemies"}]),
         OpSpec("duplicate_node", handlers.addon_duplicate_node, "Duplica nó", {"node_path": {"type": "string", "required": True}}, [{"node_path": "./Enemy"}]),
         OpSpec("batch_edit", handlers.addon_batch_edit, "Edição em lote", {"operations": {"type": "array", "required": True}}, [{"operations": [{"op": "create", "type": "Sprite2D"}]}]),
         OpSpec("take_screenshot", handlers.addon_take_screenshot, "Screenshot via editor", {"file_path": {"type": "string", "required": False}}, [{}]),
         OpSpec("get_scene_tree", handlers.addon_get_scene_tree, "Árvore de cena", {}, [{}])],
    tags=["editor", "addon", "godot"])
