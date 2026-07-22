"""domains/gamestate/manifest.py — F5.22."""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="gamestate", tool_name="gamestate_manage", title="Game State", namespace="project", version="1.0.0",
    description="Gerencia estado: save system, dados, FSM e transições.\nQUANDO USAR: para persistência e máquinas de estado.\nQUANDO NÃO USAR: para inventário (use inventory_manage).",
    phases=[Phase.CONTEUDO], annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("create_save", handlers.create_save_system, "Cria sistema de save", {"scene_path": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn"}]),
         OpSpec("define_save", handlers.define_save_data, "Define dados de save", {"scene_path": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn", "data_name": "player_save"}]),
         OpSpec("create_fsm", handlers.create_state_machine, "Cria máquina de estados", {"scene_path": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn", "states": ["idle", "run", "attack"]}]),
         OpSpec("add_transition", handlers.add_state_transition, "Adiciona transição FSM", {"scene_path": {"type": "string", "required": True}, "from_state": {"type": "string", "required": True}, "to_state": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn", "from_state": "idle", "to_state": "run", "condition": "is_moving"}])],
    tags=["save", "fsm", "estado"])
