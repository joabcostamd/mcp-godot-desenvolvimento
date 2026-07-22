"""domains/script/manifest.py"""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="script", tool_name="script_manage", title="Scripts", namespace="project", version="1.0.0",
    description="Gerencia scripts GDScript: gerar, anexar, desanexar, validar, variáveis e sinais.\nQUANDO USAR: para lógica de jogo.\nQUANDO NÃO USAR: para edição direta (use read_file/write_file).",
    phases=[Phase.DESIGN, Phase.PROTOTIPO], annotations={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("generate", handlers.generate_gdscript, "Gera template", {"class_name": {"type": "string", "required": False}}, [{"class_name": "Player", "extends": "CharacterBody2D"}]),
         OpSpec("attach", handlers.attach_script, "Anexa script a nó", {"scene_path": {"type": "string", "required": True}, "node_path": {"type": "string", "required": True}, "script_path": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn", "node_path": "./Player", "script_path": "res://scripts/player.gd"}]),
         OpSpec("detach", handlers.detach_script, "Desanexa script", {"scene_path": {"type": "string", "required": True}, "node_path": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn", "node_path": "./Player"}]),
         OpSpec("validate", handlers.validate_gdscript_syntax, "Valida sintaxe", {"script_path": {"type": "string", "required": True}}, [{"script_path": "res://scripts/player.gd"}]),
         OpSpec("add_var", handlers.add_script_variable, "Adiciona variável", {"scene_path": {"type": "string", "required": True}, "node_path": {"type": "string", "required": True}, "var_name": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn", "node_path": "./Player", "var_name": "speed", "var_type": "float", "default_value": 400}]),
         OpSpec("add_signal", handlers.add_script_signal, "Adiciona sinal", {"scene_path": {"type": "string", "required": True}, "node_path": {"type": "string", "required": True}, "signal_name": {"type": "string", "required": True}}, [{"scene_path": "scenes/game.tscn", "node_path": "./Player", "signal_name": "health_changed"}])],
    tags=["gdscript", "script", "código"])
