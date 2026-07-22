"""domains/project/manifest.py"""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="project", tool_name="project_manage", title="Projeto", namespace="project", version="1.0.0",
    description="Gerencia o projeto Godot: criar, definir ativo, configurações e cena principal.\nQUANDO USAR: no início de todo jogo.\nQUANDO NÃO USAR: para input actions (use config_manage).",
    phases=[Phase.IDEIA, Phase.DESIGN], annotations={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("create", handlers.create_project, "Cria projeto", {"project_name": {"type": "string", "required": True}}, [{"project_name": "MeuJogo"}]),
         OpSpec("set_active", handlers.set_active_project, "Define projeto ativo", {"project_path": {"type": "string", "required": True}}, [{"project_path": "./MeuJogo"}]),
         OpSpec("get_settings", handlers.get_project_settings, "Lê configurações", {}, [{}]),
         OpSpec("set_setting", handlers.set_project_setting, "Define configuração", {"key": {"type": "string", "required": True}, "value": {"type": "string", "required": True}}, [{"key": "application/config/name", "value": "Meu Jogo"}]),
         OpSpec("set_main_scene", handlers.set_main_scene, "Define cena principal", {"scene_path": {"type": "string", "required": True}}, [{"scene_path": "res://scenes/main.tscn"}])],
    tags=["projeto", "godot", "config"])
