"""domains/config/manifest.py — F5.23."""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="config", tool_name="config_manage", title="Configurações", namespace="project", version="1.0.0",
    description="Gerencia configurações: input actions e autoloads.\nQUANDO USAR: para mapear controles e singletons.\nQUANDO NÃO USAR: para sinais (use node_manage).",
    phases=[Phase.DESIGN], annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("input_action", handlers.configure_input_action, "Configura Input Map", {"action_name": {"type": "string", "required": True}, "key": {"type": "string", "required": False}}, [{"action_name": "jump", "key": "Space"}]),
         OpSpec("autoload", handlers.configure_autoload, "Configura Autoload/Singleton", {"script_path": {"type": "string", "required": True}}, [{"script_path": "res://globals/GameManager.gd"}])],
    tags=["config", "input", "autoload"])
