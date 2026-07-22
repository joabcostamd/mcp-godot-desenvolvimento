"""domains/scene/manifest.py"""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="scene", tool_name="scene_manage", title="Cenas", namespace="project", version="1.0.0",
    description="Gerencia cenas Godot (.tscn): criar, carregar árvore e instanciar sub-cenas.\nQUANDO USAR: para criar e manipular cenas.\nQUANDO NÃO USAR: para nós individuais (use node_manage).",
    phases=[Phase.DESIGN, Phase.PROTOTIPO, Phase.CONTEUDO], annotations={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("create", handlers.create_scene, "Cria cena nova", {"scene_name": {"type": "string", "required": True}}, [{"scene_name": "game"}]),
         OpSpec("load_tree", handlers.load_scene_tree, "Carrega árvore da cena", {"scene_path": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn"}]),
         OpSpec("instance", handlers.instance_scene_as_child, "Instancia sub-cena", {"scene_path": {"type": "string", "required": True}, "parent_node_path": {"type": "string", "required": True}, "instance_path": {"type": "string", "required": True}}, [{"scene_path": "scenes/main.tscn", "parent_node_path": ".", "instance_path": "res://scenes/enemy.tscn"}])],
    tags=["cena", "godot", "tscn"])
