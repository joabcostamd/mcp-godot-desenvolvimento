"""domains/inventory/manifest.py — F5.20."""
from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(domain="inventory", tool_name="inventory_manage", title="Gerenciar Inventário", namespace="project", version="1.0.0",
    description=("Gerencia inventário: criar sistema, definir itens e interface de slots.\nQUANDO USAR: para sistemas de coleta, loja e equipamento.\nQUANDO NÃO USAR: para save/load (use gamestate_manage).\nPRÉ-CONDIÇÕES: cena alvo.\nERRO COMUM: item_id duplicado."),
    phases=[Phase.DESIGN, Phase.CONTEUDO], annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("create_system", handlers.create_inventory_system, "Cria sistema de inventário", {"scene_path": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn"}], "safety_manage(op=undo)"),
         OpSpec("define_item", handlers.define_inventory_item, "Define um item (id, nome, tipo, stack)", {"scene_path": {"type": "string", "required": True}, "item_id": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn", "item_id": "hp_potion", "item_name": "Poção de Vida"}], "safety_manage(op=undo)"),
         OpSpec("create_ui", handlers.create_inventory_ui, "Cria interface de inventário", {"scene_path": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn"}], "safety_manage(op=undo)")],
    tags=["inventário", "itens", "rpg", "ui"])
